"""Deterministic language router. No LLM, eval, shell, network or arbitrary models."""
import re
from typing import Callable

TOOLS = {
    'list_datasets': 'List the synthetic demo datasets.',
    'describe_dataset': 'Describe and preview actual generated synthetic demo inputs.',
    'run_demo_analysis': 'Execute the fixed synthetic Stage-A analysis with the selected project default model.',
    'compare_runs': 'Compare the two validated predefined models in a selected existing run.',
    'summarize_diagnostics': 'Explain actual diagnostics and limitations of an existing run.',
    'resume_workspace': 'Read the selected project context and reverify its latest stored result.',
}
PHRASES = {
    'welche datensätze gibt es': 'list_datasets',
    'zeige den beispieldatensatz': 'describe_dataset',
    'starte die mmm-analyse': 'run_demo_analysis',
    'vergleiche die beiden modellläufe': 'compare_runs',
    'erkläre die warnungen und die modellgrenzen': 'summarize_diagnostics',
    'wo haben wir aufgehört': 'resume_workspace',
    'where did we leave off': 'resume_workspace',
}

PERMISSIONS = {name: 'compute_fixed_synthetic' if name == 'run_demo_analysis' else 'read_selected_project'
               for name in TOOLS}


def resolve(message):
    if not isinstance(message, str) or len(message) > 200:
        raise ValueError('Please use one of the supported example requests.')
    normalized = ' '.join(message.strip().casefold().split()).rstrip('.!?')
    if normalized not in PHRASES:
        raise ValueError('Anfrage nicht unterstützt. Bitte verwende eine der vier angebotenen Anfragen; freie Befehle, Datenabrufe oder Modelländerungen sind nicht verfügbar.')
    return PHRASES[normalized]


def call_tool(name: str, arguments: dict, handlers: dict[str, Callable]):
    """Tested adapter seam for a future MCP transport; NOT an MCP server."""
    if name not in TOOLS or name not in handlers:
        raise ValueError('Tool is not allowlisted')
    expected = {'run_id'} if name in ('compare_runs', 'summarize_diagnostics') else set()
    if set(arguments) != expected:
        raise ValueError('Unexpected tool arguments')
    if expected and (not isinstance(arguments['run_id'], str) or not re.fullmatch(r'[0-9a-f]{32}', arguments['run_id'])):
        raise ValueError('Invalid run ID')
    return handlers[name](**arguments)


def respond(message, run_id, handlers):
    name = resolve(message)
    if name in ('compare_runs', 'summarize_diagnostics') and not run_id:
        return dict(status='needs_analysis', tool=name, executed=False,
                    text='Noch kein Ergebnis ausgewählt. Starte zuerst die MMM-Analyse.', output=None)
    output = call_tool(name, {'run_id': run_id} if name in ('compare_runs', 'summarize_diagnostics') else {}, handlers)
    if name == 'list_datasets':
        text = f"{len(output)} Datensatz verfügbar: " + ', '.join(d['name'] for d in output) + '. Ausschließlich synthetisch.'
    elif name == 'describe_dataset':
        text = (f"{output['total_months']} synthetische Monate; Vorschau der ersten {output['preview_months']}. "
                f"Seed {output['metadata']['seed']}. Die Vorschau stammt aus dem tatsächlichen Generator, ohne Fit.")
    elif name == 'run_demo_analysis':
        text = output['interpretation']
    elif name == 'compare_runs':
        c = output['comparison']
        text = (f"Beide Modelle verwenden dieselben Daten und denselben Holdout. "
                f"RMSE-Differenz ohne minus mit Quartalsende: {c['test_rmse_delta_right_minus_left']:.2f}. "
                'Dies ist eine synthetische Sensitivitätsprüfung, kein kausaler Marketingeffekt.')
    elif name == 'resume_workspace':
        text = output['summary']
    else:
        text = (f"Rang {output['diagnostics']['rank']}/{output['diagnostics']['design_columns']}; "
                f"skalierte Konditionszahl {output['diagnostics']['scaled_condition_number']:.2f}. "
                + ' '.join(output['warnings']))
    return dict(status='completed', tool=name, executed=True, text=text, output=output)
