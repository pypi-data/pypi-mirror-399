"""
Command-line interface for medimagecleaner
"""

import argparse
import sys
from pathlib import Path
from medimagecleaner import BatchProcessor, __version__


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="De-identify medical images (DICOM files)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic de-identification
  medimagecleaner --input ./raw --output ./clean
  
  # With text removal and validation
  medimagecleaner --input ./raw --output ./clean --remove-text --validate
  
  # Convert to PNG format
  medimagecleaner --input ./raw --output ./clean --format png
  
  # Custom log directory
  medimagecleaner --input ./raw --output ./clean --log-dir ./my_logs
        """
    )
    
    # Version
    parser.add_argument(
        "--version",
        action="version",
        version=f"medimagecleaner {__version__}"
    )
    
    # Required arguments
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input directory containing DICOM files"
    )
    
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output directory for de-identified files"
    )
    
    # Optional processing steps
    parser.add_argument(
        "--remove-text",
        action="store_true",
        help="Remove burned-in text from images"
    )
    
    parser.add_argument(
        "--text-method",
        choices=["ocr", "crop", "edges"],
        default="ocr",
        help="Method for text removal (default: ocr)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["png", "jpg", "jpeg", "tiff", "npy"],
        help="Convert to specified format (default: keep as DICOM)"
    )
    
    # Validation
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate de-identified files"
    )
    
    parser.add_argument(
        "--validation-sample-rate",
        type=float,
        default=0.1,
        help="Fraction of files to validate (0.0-1.0, default: 0.1)"
    )
    
    # Logging
    parser.add_argument(
        "--log-dir",
        default="./deidentification_logs",
        help="Directory for audit logs (default: ./deidentification_logs)"
    )
    
    parser.add_argument(
        "--no-logging",
        action="store_true",
        help="Disable audit logging"
    )
    
    # Other options
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't process subdirectories recursively"
    )
    
    parser.add_argument(
        "--report",
        help="Path to save final report (optional)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    input_dir = Path(args.input)
    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}", file=sys.stderr)
        return 1
    
    # Initialize processor
    print(f"medimagecleaner v{__version__}")
    print("=" * 60)
    
    processor = BatchProcessor(
        log_dir=args.log_dir,
        enable_logging=not args.no_logging,
        enable_validation=args.validate
    )
    
    # Process directory
    print(f"Input:  {input_dir}")
    print(f"Output: {args.output}")
    print(f"Steps:  ", end="")
    steps = ["metadata removal"]
    if args.remove_text:
        steps.append(f"text removal ({args.text_method})")
    if args.format:
        steps.append(f"convert to {args.format}")
    if args.validate:
        steps.append("validation")
    print(", ".join(steps))
    print("=" * 60)
    
    try:
        results = processor.process_directory(
            input_dir=input_dir,
            output_dir=args.output,
            remove_metadata=True,
            remove_burned_text=args.remove_text,
            convert_format=args.format,
            text_removal_method=args.text_method,
            validate_output=args.validate,
            recursive=not args.no_recursive,
            validation_sample_rate=args.validation_sample_rate
        )
        
        # Print summary
        print("\nResults:")
        print(f"  Total files:  {results['total_files']}")
        print(f"  Successful:   {results['successful']}")
        print(f"  Failed:       {results['failed']}")
        
        if results['total_files'] > 0:
            success_rate = results['successful'] / results['total_files'] * 100
            print(f"  Success rate: {success_rate:.1f}%")
        
        # Validation summary
        if args.validate and results.get('validation_results'):
            val = results['validation_results']
            print(f"\nValidation:")
            print(f"  Files checked: {val.get('files_checked', 0)}")
            print(f"  Passed:        {val.get('passed', 0)}")
            print(f"  Failed:        {val.get('failed', 0)}")
        
        # Generate report
        report_path = args.report or f"{args.output}/deidentification_report.txt"
        report = processor.generate_complete_report(results, report_path)
        print(f"\nReport saved to: {report_path}")
        
        # Warnings
        if results['failed'] > 0:
            print("\n⚠️  Some files failed processing. Check the report for details.")
            return 1
        
        if args.validate and results.get('validation_results', {}).get('failed', 0) > 0:
            print("\n⚠️  Some files failed validation. Review manually before use.")
            return 1
        
        print("\n✓ De-identification complete!")
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
