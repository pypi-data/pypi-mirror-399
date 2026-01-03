"""
Command-line interface for Meitei Senter.
"""

import argparse
import sys


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="meitei-senter",
        description="Split Meitei Mayek text into sentences"
    )
    parser.add_argument(
        "--text", "-t",
        type=str,
        help="Text to split into sentences"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--neural", "-n",
        action="store_true",
        help="Use neural network model (experimental)"
    )
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version and exit"
    )
    
    args = parser.parse_args()
    
    if args.version:
        from . import __version__
        print(f"meitei-senter {__version__}")
        return 0
    
    # Load the splitter
    from . import load_splitter
    
    print("Loading sentence splitter...")
    try:
        if args.neural:
            from .model import MeiteiSentenceSplitter
            import os
            model_dir = os.path.dirname(__file__)
            splitter = MeiteiSentenceSplitter(
                pth_path=os.path.join(model_dir, "meitei_senter.pth"),
                spm_path=os.path.join(model_dir, "meitei_tokenizer.model"),
                config_path=os.path.join(model_dir, "meitei_senter.json"),
                use_neural=True
            )
        else:
            from .model import MeiteiSentenceSplitter
            import os
            model_dir = os.path.dirname(__file__)
            splitter = MeiteiSentenceSplitter(
                spm_path=os.path.join(model_dir, "meitei_tokenizer.model")
            )
    except Exception as e:
        print(f"Error loading model: {e}")
        return 1
    
    print("Ready!\n")
    
    if args.text:
        sentences = splitter.split_sentences(args.text)
        print("Sentences:")
        for i, sent in enumerate(sentences, 1):
            print(f"  {i}. {sent}")
    
    if args.interactive or not args.text:
        print("Interactive mode. Type 'quit' to exit.\n")
        while True:
            try:
                text = input("Enter text: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            
            if text.lower() == "quit":
                break
            if not text:
                continue
            
            sentences = splitter.split_sentences(text)
            print(f"\nFound {len(sentences)} sentence(s):")
            for i, sent in enumerate(sentences, 1):
                print(f"  {i}. {sent}")
            print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
