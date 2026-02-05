from automata.fa.dfa import DFA

dfa = DFA(
    states={'q0', 'q1'},
    input_symbols={'0', '1'},
    transitions={
        'q0': {'0': 'q0', '1': 'q1'},
        'q1': {'0': 'q0', '1': 'q1'}
    },
    initial_state='q0',
    final_states={'q0'}
)

try:
    minimized = dfa.minimize()
    print("Minimize worked! States:", minimized.states)
except AttributeError as e:
    print("Error:", e)
except Exception as e:
    print("Other error:", e)