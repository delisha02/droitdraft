import pdfplumber
import sys

def main():
    try:
        # Force utf-8 for output
        sys.stdout.reconfigure(encoding='utf-8')
        with pdfplumber.open('d:/droitdraft/Death-Certificate.pdf') as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages])
            print(text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
