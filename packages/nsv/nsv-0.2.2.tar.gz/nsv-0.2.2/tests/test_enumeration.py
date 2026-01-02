import random
from collections import Counter

import nsv
from nsv import Writer, Reader


pre_enc_cell_pool = ('\\', '\n', 'n')
post_enc_cell_pool = ('\\\\', '\\n', 'n')
post_enc_invalid_cell_pool = ('\\', 'n')

def cell(n, cell_char_pool):
    if n == 0:
        return ""
    result = []
    base = len(cell_char_pool)
    while n > 0:
        digit = n % base
        result.append(cell_char_pool[digit])
        n //= base
    return ''.join(result)

def singleton_seqseq(_cell: str) -> list[list[str]]:
    return [[_cell]]

def seqseq(n, cell_char_pool):
    res = []
    cur = []
    for _ in range(n):
        if random.random() < 0.5:
            res.append(cur)
            cur = []
        cur.append(cell(random.randint(0, 100), cell_char_pool))
    res.append(cur)
    return res

def generate_valid_nsv(max_cells=50):
    pools = ['\n', '\\', 'a']  # newline, backslash, regular char
    
    test_strings = []
    
    # Start with empty data
    test_strings.append(nsv.dumps([]))
    
    # Generate single-row NSV files with increasing cell counts
    for num_cells in range(1, max_cells):
        cell_contents = []
        
        # Generate all combinations for this number of cells
        # For simplicity, start with just the first few patterns per cell
        for cell_idx in range(num_cells):
            # Use a simple pattern for each cell position
            pattern_num = cell_idx % 10  # Cycle through first 10 patterns
            cell_content = cell(pattern_num)
            cell_contents.append(cell_content)
        
        # Create data structure and get canonical NSV
        data = [cell_contents]
        nsv_string = nsv.dumps(data)
        test_strings.append(nsv_string)
    
    # Add a few multi-row examples
    for num_rows in range(2, 4):
        for num_cols in range(1, 4):
            data = []
            for row in range(num_rows):
                row_data = []
                for col in range(num_cols):
                    pattern_num = (row * num_cols + col) % 10
                    cell_content = cell(pattern_num)
                    row_data.append(cell_content)
                data.append(row_data)
            
            nsv_string = nsv.dumps(data)
            test_strings.append(nsv_string)
    
    return test_strings

def generate_test_strings(max_num=1000):
    """Generate test strings covering edge cases systematically."""
    return generate_valid_nsv(50)

def test_round_trip(test_strings):
    """Test that loads/dumps round-trip works for all NSV format strings."""
    failures = []
    
    for i, original_nsv in enumerate(test_strings):
        try:
            # Test round-trip: NSV string -> data -> NSV string
            loaded_data = nsv.loads(original_nsv)
            dumped_nsv = nsv.dumps(loaded_data)
            
            if original_nsv != dumped_nsv:
                failures.append({
                    'index': i,
                    'original_nsv': repr(original_nsv),
                    'loaded_data': loaded_data,
                    'dumped_nsv': repr(dumped_nsv)
                })
                
        except Exception as e:
            failures.append({
                'index': i,
                'original_nsv': repr(original_nsv),
                'error': str(e)
            })
    
    return failures

if __name__ == "__main__":
    for i in range(100):
        s = cell(i, pre_enc_cell_pool)
        es = Writer.escape(s)
        s2 = Reader.unescape(es)
        if s != s2:
            print(i, s, es, s2, sep='\n')
    print("Generating structures")
    sss = [seqseq(10000, pre_enc_cell_pool) for _ in range(100)]
    for ss in sss:
        if nsv.loads(nsv.dumps(ss)) != ss:
            print(ss)
            print(nsv.loads(nsv.dumps(ss)))
        # print(nsv.dumps(ss))

    # print("Generating systematic test cases...")
    # test_strings = generate_test_strings(1000)
    #
    # print(f"Generated {len(test_strings)} test strings")
    # print("Sample strings:")
    # for i, s in enumerate(test_strings[:20]):
    #     print(f"{i:3d}: {repr(s)}")
    #
    # print("\nRunning round-trip tests...")
    # failures = test_round_trip(test_strings)
    #
    # if failures:
    #     print(f"Found {len(failures)} failures:")
    #     for failure in failures[:10]:  # Show first 10 failures
    #         print(f"  {failure}")
    # else:
    #     print("All tests passed!")