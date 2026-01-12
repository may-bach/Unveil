class Teacher:
    def __init__(self):
        # Example: language of even number of 1s
        self.alphabet = ['0', '1']
        self.start = 'q0'
        self.accept = {'q0'}
        self.delta = {
            'q0': {'0': 'q0', '1': 'q1'},
            'q1': {'0': 'q1', '1': 'q0'}
        }

    def membership_query(self, s):
        state = self.start
        for char in s:
            state = self.delta[state][char]
        return state in self.accept


class ObservationTable:
    def __init__(self, alphabet):
        self.alphabet = alphabet
        self.S = {""}                # prefixes (states)
        self.E = {""}                # suffixes (experiments)
        self.table = {}              # (prefix, suffix) -> bool

    def ask(self, teacher, prefix, suffix):
        key = (prefix, suffix)
        if key not in self.table:
            full_string = prefix + suffix
            self.table[key] = teacher.membership_query(full_string)
        return self.table[key]

    def fill(self, teacher):
        # Fill all current cells
        all_prefixes = list(self.S) + [p + a for p in self.S for a in self.alphabet]
        for prefix in set(all_prefixes):
            for suffix in self.E:
                self.ask(teacher, prefix, suffix)

    def print_table(self):
        prefixes = sorted(list(self.S) + [p + a for p in self.S for a in self.alphabet])
        suffixes = sorted(self.E)
        print("\nObservation Table:")
        print("Prefix".ljust(6) + " | " + "  ".join(f"{s:>4}" for s in suffixes))
        print("-" * (6 + len(suffixes) * 6))
        for p in prefixes:
            row = []
            for s in suffixes:
                val = self.table.get((p, s), "?")
                row.append("1" if val else "0")
            print(f"{p:>6} | " + "  ".join(row))

    def get_row_signature(self, prefix):
        suffixes = sorted(self.E)  # consistent order!
        return tuple(self.table.get((prefix, s), False) for s in suffixes)

    def is_closed(self):
        s_signatures = {self.get_row_signature(p) for p in self.S}
        
        for prefix in list(self.S):
            for a in self.alphabet:
                extended = prefix + a

                self.fill(teacher)
                 
                ext_sig = self.get_row_signature(extended)
                
                if ext_sig not in s_signatures:
                    return False, extended
        
        return True, None


if __name__ == "__main__":
    teacher = Teacher()
    table = ObservationTable(['0', '1'])

    # Initialize with epsilon
    table.S = {""}
    table.E = {"", "1"}  # two suffixes to start

    print("Initial fill...")
    table.fill(teacher)
    table.print_table()

    closed, witness = table.is_closed()
    print("\nClosure check:")
    if closed:
        print("Table is CLOSED ✓")
        print("All extended prefixes already match existing states.")
    else:
        print("Table is NOT closed ✗")
        print(f"New state candidate: '{witness}'")
        print("→ Next step: add this prefix to S and refill")