
from vidai.utils import get_media_type

def test_bad_inputs():
    print("Testing bad inputs...")
    try:
        get_media_type("document.pdf")
        print("FAIL: Should have raised ValueError for pdf")
    except ValueError as e:
        print(f"PASS: Caught expected error for pdf: {e}")

    try:
        get_media_type("spreadsheet.xlsx")
        print("FAIL: Should have raised ValueError for xlsx")
    except ValueError as e:
        print(f"PASS: Caught expected error for xlsx: {e}")
        
    try:
        get_media_type("unknown_file")
        print("FAIL: Should have raised ValueError for unknown")
    except ValueError as e:
        print(f"PASS: Caught expected error for unknown: {e}")
        
    print("Test Complete.")

if __name__ == "__main__":
    test_bad_inputs()
