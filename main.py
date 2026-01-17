from graphviz import Digraph
import random

class Teacher:
    def __init__(self):
        self.alphabet = ['0', '1']

    def membership_query(self, s):
        ones_count = 0
        for char in s:
            if char == '1':
                ones_count += 1
        cond1 = (ones_count % 2 == 0)

        zeros_count = len(s) - ones_count
        cond2 = (zeros_count % 3 == 0)

        cond3 = '111' not in s

        return cond1 and cond2 and cond3

    def equivalence_query(self, hypothesis):
        
        for _ in range(500):
            length = random.randint(0, 30)
            s = ''.join(random.choice(self.alphabet) for _ in range(length))
            teacher_accept = self.membership_query(s)
            hypo_accept = hypothesis.membership_query(s)
            if teacher_accept != hypo_accept:
                return s
        return None


class ObservationTable:
    def __init__(self, alphabet):
        self.alphabet = alphabet
        self.S = {""} 
        self.E = {""}   
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
    
    def render_graphviz(self, filename="learned_dfa"):
        """Render the DFA with improved layout and colors"""
        from graphviz import Digraph

        dot = Digraph(comment='Learned DFA', format='png')
        dot.attr(rankdir='LR')           # Left to right
        dot.attr('graph', splines='curved')  # Smooth curved edges
        dot.attr('graph', overlap='false')   # Prevent node overlap
        dot.attr('graph', nodesep='0.6')     # Horizontal spacing
        dot.attr('graph', ranksep='1.2')     # Vertical spacing
        dot.attr('node', fontsize='14', fontname='Arial')

        # States
        for state in sorted(self.states, key=lambda s: int(s[1:]) if s.startswith('q') else 999):
            shape = 'doublecircle' if state in self.accept_states else 'circle'
            fillcolor = 'lightgreen' if state in self.accept_states else 'white'
            dot.node(state, state, shape=shape, style='filled', fillcolor=fillcolor)

        # Invisible start node + arrow
        dot.node('start', shape='none')
        dot.edge('start', self.start_state, arrowhead='normal', style='bold')

        
        for state in self.states:
            for char, target in sorted(self.transitions[state].items()):
                color = 'blue' if char == '0' else 'red'
                dot.edge(state, target, label=char, color=color, fontcolor=color, fontsize='12')

        # Render both PNG and SVG
        dot.render(filename, format='png', view=True, cleanup=True)
        dot.render(filename, format='svg', cleanup=False)  # Keep .svg file too
        print(f"DFA saved as {filename}.png (opened) and {filename}.svg")


if __name__ == "__main__":
    teacher = Teacher()
    table = ObservationTable(teacher.alphabet)

    print("Starting L* learning...")

    iteration = 0
    while True:
        iteration += 1
        print(f"\n=== Iteration {iteration} ===")

        table.fill(teacher)
        while True:
            closed, witness = table.is_closed(teacher)
            if closed:
                print("Table is CLOSED ✓")
                break
            print(f"  Adding new prefix '{witness}'")
            table.S.add(witness)
            table.fill(teacher)

        while True:
            consistent, new_suffix = table.is_consistent(teacher)
            if consistent:
                print("Table is CONSISTENT ✓")
                break
            print(f"  Adding new suffix '{new_suffix}'")
            table.E.add(new_suffix)
            table.fill(teacher)

        hypothesis = table.construct_hypothesis_dfa()
        print("\nCurrent Hypothesis:")
        hypothesis.print_dfa_table()

        hypothesis.render_graphviz("learned_dfa")

        counterexample = teacher.equivalence_query(hypothesis)
        if counterexample is None:
            print("\nSUCCESS! Hypothesis is equivalent to the hidden DFA.")
            print("Final DFA:")
            hypothesis.print_dfa_table()
            break
        else:
            print(f"\nCounterexample found: '{counterexample}'")
            for i in range(len(counterexample) + 1):
                prefix = counterexample[:i]
                if prefix not in table.S:
                    print(f"  → Adding prefix '{prefix}' from counterexample")
                    table.S.add(prefix)
            table.fill(teacher)

        print(f"\nSUCCESS! Learned in {iteration} iterations.")
        
    print("\nTest some strings:")
    test_strings = [
        ("", True),
        ("0", False),
        ("00", False),
        ("000", True),
        ("1", False),
        ("11", True),
        ("111", False),
        ("00011", True),
        ("1110", False),
        ("000000", True),
        ("101010", False),
        ("11111", False),
        ("000011", False)
    ]
    for s, expected in test_strings:
        result = hypothesis.membership_query(s)
        print(f"'{s:6}' → {result}   (expected: {expected})")