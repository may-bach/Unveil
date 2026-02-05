from graphviz import Digraph
import random
import difflib
import re

class Teacher:
    def __init__(self):
        self.alphabet = ['0', '1']
        self.rule_description = input("\nEnter the condition/rule to learn (be casual, typos ok, e.g. 'odd ones and zeros'): ").lower().strip()
        self.parse_rule()

    def parse_rule(self):
        synonyms = {
            'even': ['even', 'pair', 'evenly', 'paired', 'parity even', 'even parity'],
            'odd': ['odd', 'uneven', 'oddly', 'unpaired', 'parity odd'],
            'number': ['number', 'count', 'amount', 'how many', 'quantity', 'total'],
            'ones': ['1s', '1', 'ones', 'one', '1\'s'],
            'zeros': ['0s', '0', 'zeros', 'zero', '0\'s', 'zeroes'],
            'ends with': ['ends with', 'end with', 'finishes with', 'ending with', 'last', 'ends in', 'finish in', 'conclude with'],
            'starts with': ['starts with', 'begin with', 'beginning with', 'start in', 'begins in'],
            'contains': ['contains', 'has', 'include', 'includes', 'contain', 'have'],
            'no': ['no', 'without', 'not', 'avoid', 'does not have', 'free of'],
            'consecutive': ['consecutive', 'in a row', 'row', 'back to back', 'back-to-back', 'consec', 'straight'],
            'multiple of': ['multiple of', 'divisible by', 'modulo', 'mod', 'remainder 0', 'div by'],
            'length': ['length', 'size', 'long', 'string length']
        }

        templates = {
            'even_ones': "even number of 1s",
            'odd_ones': "odd number of 1s",
            'even_zeros': "even number of 0s",
            'odd_zeros': "odd number of 0s",
            'ends_with': "ends with",
            'starts_with': "starts with",
            'contains': "contains",
            'no_consecutive': "no consecutive",
            'mod_zero': "multiple of",
            'even_length': "length even",
            'odd_length': "length odd"
        }

        delimiters = r'\band\b|\+|&|,'
        parts = re.split(delimiters, self.rule_description)
        parts = [p.strip() for p in parts if p.strip()]

        self.conditions = []
        last_parity = None

        for part in parts:
            part_clean = part.lower().strip()
            best_match = None
            best_score = 0
            matched_template = None

            for cond_type, template in templates.items():
                score = difflib.SequenceMatcher(None, part_clean, template).ratio()
                for word in part_clean.split():
                    for key, syn_list in synonyms.items():
                        if any(difflib.SequenceMatcher(None, word, syn).ratio() > 0.8 for syn in syn_list):
                            score += 0.25
                if score > best_score:
                    best_score = score
                    best_match = cond_type
                    matched_template = template

            if best_score > 0.65:
                print(f"Matched '{part}' to '{matched_template}' (score: {best_score:.2f})")

                if best_match in ['even_ones', 'odd_ones', 'even_zeros', 'odd_zeros']:
                    last_parity = 'even' if 'even' in best_match else 'odd'
                    self.conditions.append((best_match, None))
                elif best_match in ['even_length', 'odd_length']:
                    self.conditions.append((best_match, None))
                elif best_match == 'ends_with':
                    ending = re.search(r'(?:ends? with|ending with|end with|finish with|finishes with|last)\s+([01]+)', part_clean)
                    ending_str = ending.group(1) if ending else '00'
                    self.conditions.append(('ends_with', ending_str))
                elif best_match == 'starts_with':
                    starting = re.search(r'(?:starts? with|beginning with|start with)\s+([01]+)', part_clean)
                    start_str = starting.group(1) if starting else '00'
                    self.conditions.append(('starts_with', start_str))
                elif best_match == 'contains':
                    contains_str = re.search(r'(?:contains|has|include)\s+([01]+)', part_clean)
                    substr = contains_str.group(1) if contains_str else '00'
                    self.conditions.append(('contains', substr))
                elif best_match == 'no_consecutive':
                    num_match = re.search(r'(\d+)', part_clean)
                    num = int(num_match.group(1)) if num_match else 3
                    char = '1' if '1' in part_clean else '0'
                    self.conditions.append(('no_consecutive', (num, char)))
                elif best_match == 'mod_zero':
                    mod_match = re.search(r'(\d+)', part_clean)
                    mod = int(mod_match.group(1)) if mod_match else 3
                    char = '0' if '0' in part_clean else '1'
                    self.conditions.append(('mod_zero', (char, mod)))
            else:
                # Carry-over with fuzzy tolerance
                if last_parity:
                    zero_variations = ['zeros', 'zero', '0s', '0', '0\'s', 'zeors', 'zros', 'zeroes']
                    one_variations = ['ones', 'one', '1s', '1', '1\'s']
                    zero_score = max(difflib.SequenceMatcher(None, word, var).ratio() 
                                     for word in part_clean.split() 
                                     for var in zero_variations)
                    one_score = max(difflib.SequenceMatcher(None, word, var).ratio() 
                                    for word in part_clean.split() 
                                    for var in one_variations)

                    if zero_score > 0.75:
                        print(f"Carrying '{last_parity}' to 'zeros' part (score: {zero_score:.2f})")
                        cond = f'{last_parity}_zeros'
                        self.conditions.append((cond, None))
                    elif one_score > 0.75:
                        print(f"Carrying '{last_parity}' to 'ones' part (score: {one_score:.2f})")
                        cond = f'{last_parity}_ones'
                        self.conditions.append((cond, None))
                    else:
                        print(f"Warning: Skipped unclear part '{part}' (score too low)")
                else:
                    print(f"Warning: Skipped unclear part '{part}' (score too low)")

        if not self.conditions:
            print("No valid conditions matched — defaulting to 'even number of 1s'")
            self.conditions = [('even_ones', None)]

    def membership_query(self, s):
        for cond_type, param in self.conditions:
            if cond_type == 'even_ones':
                if s.count('1') % 2 != 0:
                    return False
            elif cond_type == 'odd_ones':
                if s.count('1') % 2 == 0:
                    return False
            elif cond_type == 'even_zeros':
                if (len(s) - s.count('1')) % 2 != 0:
                    return False
            elif cond_type == 'odd_zeros':
                if (len(s) - s.count('1')) % 2 == 0:
                    return False
            elif cond_type == 'ends_with':
                if not s.endswith(param):
                    return False
            elif cond_type == 'starts_with':
                if not s.startswith(param):
                    return False
            elif cond_type == 'contains':
                if param not in s:
                    return False
            elif cond_type == 'no_consecutive':
                num, char = param
                if char * num in s:
                    return False
            elif cond_type == 'mod_zero':
                char, mod = param
                count = s.count(char)
                if count % mod != 0:
                    return False
            elif cond_type == 'even_length':
                if len(s) % 2 != 0:
                    return False
            elif cond_type == 'odd_length':
                if len(s) % 2 == 0:
                    return False
        return True

    def equivalence_query(self, hypothesis):
        for _ in range(300):
            length = random.randint(0, 30)
            s = ''.join(random.choice(self.alphabet) for _ in range(length))
            if self.membership_query(s) != hypothesis.membership_query(s):
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
        self.alphabet = ['0', '1']

    def membership_query(self, string):
        state = self.start_state
        for char in string:
            if char not in self.alphabet:
                return False
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
        dot = Digraph(comment='Learned DFA', format='png')
        dot.attr(rankdir='LR')
        dot.attr('graph', splines='curved', overlap='false', nodesep='0.7', ranksep='1.3')
        dot.attr('node', fontsize='14', fontname='Arial', shape='circle')

        for state in sorted(self.states, key=lambda s: int(s[1:]) if s.startswith('q') else 999):
            shape = 'doublecircle' if state in self.accept_states else 'circle'
            fillcolor = '#ccffcc' if state in self.accept_states else 'white'
            dot.node(state, state, shape=shape, style='filled', fillcolor=fillcolor)

        dot.node('start', shape='none')
        dot.edge('start', self.start_state, arrowhead='normal', style='bold', color='blue')

        for state in self.states:
            for char, target in sorted(self.transitions[state].items()):
                color = 'blue' if char == '0' else 'red'
                dot.edge(state, target, label=char, color=color, fontcolor=color, fontsize='12')

        dot.render(filename, format='png', view=True, cleanup=True)
        dot.render(filename, format='svg', cleanup=False)
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

            print(f"\nLearned in {iteration} iterations.")

            # Infinite Interactive Test Mode
            print("\n" + "="*60)
            print("INTERACTIVE TEST MODE (loops forever)")
            print("Enter any string to test if it's accepted/rejected.")
            print("Press Ctrl+C to stop.")
            print("="*60)

            try:
                while True:
                    user_input = input("\nEnter string: ").strip()
                    result = hypothesis.membership_query(user_input)
                    status = "ACCEPTED" if result else "REJECTED"
                    print(f"→ '{user_input}' → {status}")
            except KeyboardInterrupt:
                print("\n\nCtrl+C detected — exiting gracefully.")
                print("Thanks for testing!")
                break
            break
        else:
            print(f"\nCounterexample found: '{counterexample}'")
            for i in range(len(counterexample) + 1):
                prefix = counterexample[:i]
                if prefix not in table.S:
                    print(f"  → Adding prefix '{prefix}' from counterexample")
                    table.S.add(prefix)
            table.fill(teacher)