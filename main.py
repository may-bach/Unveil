class Teacher:
    def __init__(self):
        # Language: strings with NO three consecutive 1s
        self.alphabet = ['0', '1']
        self.start = 'q0'
        self.accept = {'q0', 'q1', 'q2'}  # reject only q3
        self.delta = {
            'q0': {'0': 'q0', '1': 'q1'},
            'q1': {'0': 'q0', '1': 'q2'},
            'q2': {'0': 'q0', '1': 'q3'},
            'q3': {'0': 'q0', '1': 'q3'}  # sink state
        }

    def membership_query(self, s):
        state = self.start
        for char in s:
            state = self.delta[state][char]
        return state in self.accept

    def membership_query(self, s):
        state = self.start
        for char in s:
            state = self.delta[state][char]
        return state in self.accept
    
    def equivalence_query(self, hypothesis):
        import random
        for _ in range(100):  # You can increase this for more confidence
            length = random.randint(0, 20)
            s = ''.join(random.choice(self.alphabet) for _ in range(length))
            teacher_accept = self.membership_query(s)
            hypo_accept = hypothesis.membership_query(s)
            if teacher_accept != hypo_accept:
                return s  # Counterexample found
        return None  # No difference found (probably equivalent)


class ObservationTable:
    def __init__(self, alphabet):
        self.alphabet = alphabet
        self.S = {""} 
        self.E = {""}               # Start minimal — let algorithm grow it
        self.table = {}           

    def ask(self, teacher, prefix, suffix):
        key = (prefix, suffix)
        if key not in self.table:
            full_string = prefix + suffix
            self.table[key] = teacher.membership_query(full_string)
        return self.table[key]

    def fill(self, teacher):
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
        suffixes = sorted(self.E)
        return tuple(self.table.get((prefix, s), False) for s in suffixes)
    
    def is_closed(self, teacher): 
        self.fill(teacher)
        s_signatures = {self.get_row_signature(p) for p in self.S}
        for prefix in list(self.S):
            for a in self.alphabet:
                extended = prefix + a
                ext_sig = self.get_row_signature(extended)
                if ext_sig not in s_signatures:
                    return False, extended
        return True, None

    def is_consistent(self, teacher):
        self.fill(teacher)
        row_to_prefixes = {}
        for p in self.S:
            sig = self.get_row_signature(p)
            row_to_prefixes.setdefault(sig, []).append(p)

        for sig, group in row_to_prefixes.items():
            if len(group) < 2:
                continue
            for char in self.alphabet:
                exts = [p + char for p in group]
                ext_sigs = [self.get_row_signature(ext) for ext in exts]
                if len(set(ext_sigs)) > 1:
                    for suffix in sorted(self.E):
                        values = [self.table.get((p + char, suffix), False) for p in group]
                        if len(set(values)) > 1:
                            return False, char + suffix
                    return False, char
        return True, None
    
    def construct_hypothesis_dfa(self):
        signature_to_state = {}
        state_counter = 0

        # Assign q0 to empty string first
        empty_sig = self.get_row_signature("")
        signature_to_state[empty_sig] = "q0"
        state_counter = 1

        for prefix in sorted(self.S):
            sig = self.get_row_signature(prefix)
            if sig not in signature_to_state:
                signature_to_state[sig] = f"q{state_counter}"
                state_counter += 1

        states = set(signature_to_state.values())
        start_state = signature_to_state[empty_sig]

        accept_states = set()
        for prefix in self.S:
            if self.table.get((prefix, ""), False):
                accept_states.add(signature_to_state[self.get_row_signature(prefix)])

        transitions = {state: {} for state in states}
        for prefix in self.S:
            state = signature_to_state[self.get_row_signature(prefix)]
            for char in self.alphabet:
                extended = prefix + char
                next_sig = self.get_row_signature(extended)
                next_state = signature_to_state[next_sig]
                transitions[state][char] = next_state

        return DFA(states, start_state, accept_states, transitions)


class DFA:
    def __init__(self, states, start_state, accept_states, transitions):
        self.states = states
        self.start_state = start_state
        self.accept_states = accept_states
        self.transitions = transitions

    def membership_query(self, string):
        state = self.start_state
        for char in string:
            state = self.transitions[state][char]
        return state in self.accept_states

    def print_dfa_table(self):
        sorted_states = sorted(self.states, key=lambda s: int(s[1:]) if s.startswith('q') else 999)

        print("\n=== DFA Transition Table ===")
        print("State       |   0     |   1     | Accepting?")
        print("-" * 45)

        for state in sorted_states:
            acc = "YES ★" if state in self.accept_states else "NO"
            t0 = self.transitions[state].get('0', '-')
            t1 = self.transitions[state].get('1', '-')
            start_mark = "→ " if state == self.start_state else "  "
            print(f"{start_mark}{state:9} | {t0:7} | {t1:7} | {acc}")

        print(f"\nStart state: {self.start_state}")
        print("Accepting states: " + ", ".join(sorted(self.accept_states)) if self.accept_states else "None")


if __name__ == "__main__":
    teacher = Teacher()
    table = ObservationTable(teacher.alphabet)

    print("Starting L* learning...")

    iteration = 0
    while True:
        iteration += 1
        print(f"\n=== Iteration {iteration} ===")

        # Fill and make closed
        table.fill(teacher)
        while True:
            closed, witness = table.is_closed(teacher)
            if closed:
                print("Table is CLOSED ✓")
                break
            print(f"  Adding new prefix '{witness}'")
            table.S.add(witness)
            table.fill(teacher)

        # Make consistent
        while True:
            consistent, new_suffix = table.is_consistent(teacher)
            if consistent:
                print("Table is CONSISTENT ✓")
                break
            print(f"  Adding new suffix '{new_suffix}'")
            table.E.add(new_suffix)
            table.fill(teacher)

        # Build hypothesis
        hypothesis = table.construct_hypothesis_dfa()
        print("\nCurrent Hypothesis:")
        hypothesis.print_dfa_table()

        # Equivalence query
        counterexample = teacher.equivalence_query(hypothesis)
        if counterexample is None:
            print("\nSUCCESS! Hypothesis is equivalent to the hidden DFA.")
            print("Final DFA:")
            hypothesis.print_dfa_table()
            break
        else:
            print(f"\nCounterexample found: '{counterexample}'")
            # Add all prefixes of the counterexample
            for i in range(len(counterexample) + 1):
                prefix = counterexample[:i]
                if prefix not in table.S:
                    print(f"  → Adding prefix '{prefix}' from counterexample")
                    table.S.add(prefix)
            table.fill(teacher)