# List of supported sites names.
SUPPORTED_SITES = ['chequeado', 'cotejo']

# List of supported sites URLS.
SUPPORTED_URLS = {'chequeado': 'https://chequeado.com/', 'cotejo': 'https://cotejo.info/'}

# List of in-site supported categories.
SUPPORTED_CATEGORIES = {'chequeado': ['ultimas-noticias', 'el-explicador', 'mitos-y-enganos', 'falso-en-las-redes', 'investigaciones'],
                        'cotejo':  ['category/cotejos-breves/', 'category/cotejado-a-fondo/', 'category/regionales/']}

# List of URL page format (replace underscore with page number).
PAGE_SUFFIX = {'chequeado': "page/_/", 'cotejo': "page/_/"}

EN_SP_VERDICTS = {'TRUE': ['verdadero', 'cumplida'],
                  'mostly-TRUE': ['verdadero-pero'],
                  'FALSE': ['falso', 'insostenible'],
                  'exaggerated': ['exagerado'],
                  'deceitful': ['enganoso'],
                  'unfulfilled': ['incumplida'],
                  'hasty': ['apresurado'],
                  'questionable': ['discutible'],
                  'in progress': ['en-progreso-demorada']}