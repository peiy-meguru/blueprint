"""Color scheme for the Codeck application.

Based on: https://flatuicolors.com/palette/us
"""

from PySide6.QtGui import QColor

color = {
    'nodeLabel': QColor('#ffffff'),
    'nodeLabelBox': QColor('#3282b8'),
    'nodeBoxGradient': {
        'start': QColor('#28313b'),
        'end': QColor('#485461'),
    },
    'text': QColor('#ffffff'),
    'variable': {
        'number': QColor('#00cec9'),
        'string': QColor('#fd79a8'),
        'boolean': QColor('#d63031'),
        'array': QColor('#55efc4'),
        'data': QColor('#fdcb6e'),
    },
    'node': {
        'begin': QColor('#e17055'),
        'function': QColor('#0984e3'),
        'logic': QColor('#6c5ce7'),
        'call': QColor('#00b894'),
        'return': QColor('#e84393'),
    },
}
