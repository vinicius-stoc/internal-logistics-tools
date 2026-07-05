GROUP_DISPLAY_NAMES = {
    "LogisticaViewer": "Visualizador de Logística",
    "LogisticaAdmin": "Administrador de Logística",
}


def get_group_display_name(group_name):
    return GROUP_DISPLAY_NAMES.get(group_name, group_name)
