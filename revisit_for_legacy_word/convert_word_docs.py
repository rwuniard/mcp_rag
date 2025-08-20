#!/usr/bin/env python3
"""
Word Document Format Converter for MCP RAG Project

This script converts legacy .DOC files to .DOCX format so they can be processed
by the RAG system's Docx2txtLoader.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

def check_libreoffice_availability() -> Tuple[bool, str]:
    """Check if LibreOffice is available for document conversion."""
    try:
        import subprocess
        result = subprocess.run(['libreoffice', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, "LibreOffice command failed"
    except subprocess.TimeoutExpired:
        return False, "LibreOffice command timed out"
    except FileNotFoundError:
        return False, "LibreOffice not found in PATH"
    except Exception as e:
        return False, f"Error checking LibreOffice: {e}"

def convert_doc_to_docx(doc_path: Path, output_dir: Path) -> Tuple[bool, str]:
    """Convert a .DOC file to .DOCX using LibreOffice."""
    try:
        import subprocess
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Run LibreOffice conversion
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'docx',
            '--outdir', str(output_dir),
            str(doc_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Check if the converted file exists
            expected_output = output_dir / f"{doc_path.stem}.docx"
            if expected_output.exists():
                return True, f"Converted to {expected_output}"
            else:
                return False, f"Conversion completed but output file not found: {expected_output}"
        else:
            return False, f"LibreOffice conversion failed: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "Conversion timed out (60 seconds)"
    except Exception as e:
        return False, f"Error during conversion: {e}"

def find_doc_files(data_source_dir: Path) -> List[Path]:
    """Find all .DOC files in the data source directory."""
    doc_files = []
    for file_path in data_source_dir.glob("*.DOC"):
        if file_path.is_file() and not file_path.name.startswith('~$'):  # Skip temp files
            doc_files.append(file_path)
    
    # Also check for lowercase .doc files
    for file_path in data_source_dir.glob("*.doc"):
        if file_path.is_file() and not file_path.name.startswith('~$'):
            doc_files.append(file_path)
    
    return doc_files

def main():
    """Main conversion function."""
    print("🔄 Word Document Format Converter for MCP RAG")
    print("=" * 60)
    
    # Project paths
    project_root = Path(__file__).parent
    data_source_dir = project_root / "src" / "rag_store" / "data_source"
    
    print(f"📁 Data source directory: {data_source_dir}")
    
    if not data_source_dir.exists():
        print(f"❌ Data source directory not found: {data_source_dir}")
        sys.exit(1)
    
    # Check LibreOffice availability
    print("\n🔍 Checking LibreOffice availability...")
    libreoffice_available, version_info = check_libreoffice_availability()
    
    if not libreoffice_available:
        print(f"❌ LibreOffice not available: {version_info}")
        print("\n💡 To install LibreOffice:")
        print("   macOS: brew install --cask libreoffice")
        print("   Ubuntu: sudo apt install libreoffice")
        print("   Windows: Download from https://www.libreoffice.org/")
        sys.exit(1)
    
    print(f"✅ LibreOffice found: {version_info}")
    
    # Find .DOC files
    print("\n🔍 Scanning for .DOC files...")
    doc_files = find_doc_files(data_source_dir)
    
    if not doc_files:
        print("📭 No .DOC files found in data source directory")
        print("✅ All Word documents are already in .DOCX format or no Word docs present")
        return
    
    print(f"📝 Found {len(doc_files)} .DOC file(s) to convert:")
    for doc_file in doc_files:
        size_mb = doc_file.stat().st_size / (1024 * 1024)
        print(f"   • {doc_file.name} ({size_mb:.2f} MB)")
    
    # Convert each file
    print(f"\n🔄 Converting {len(doc_files)} file(s)...")
    successful_conversions = 0
    failed_conversions = 0
    
    for doc_file in doc_files:
        print(f"\n📄 Converting: {doc_file.name}")
        
        success, message = convert_doc_to_docx(doc_file, data_source_dir)
        
        if success:
            print(f"   ✅ {message}")
            successful_conversions += 1
            
            # Optionally remove the original .DOC file
            print(f"   🗑️  Original .DOC file kept: {doc_file.name}")
            
        else:
            print(f"   ❌ {message}")
            failed_conversions += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🎯 CONVERSION SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful conversions: {successful_conversions}")
    print(f"❌ Failed conversions: {failed_conversions}")
    
    if successful_conversions > 0:
        print(f"\n💡 Next steps:")
        print(f"   1. Run document storage: python main.py store")
        print(f"   2. Verify Word docs stored: python test_local_chroma.py")
        print(f"   3. Search Word content: python main.py search \"legal case\"")
        
        # Check if there are converted files
        docx_files = list(data_source_dir.glob("*.docx"))
        if docx_files:
            print(f"\n📝 .DOCX files now available:")
            for docx_file in docx_files:
                size_mb = docx_file.stat().st_size / (1024 * 1024)
                print(f"   • {docx_file.name} ({size_mb:.2f} MB)")
    
    if failed_conversions > 0:
        print(f"\n⚠️  Some conversions failed. Check LibreOffice installation and file permissions.")

if __name__ == "__main__":
    main()