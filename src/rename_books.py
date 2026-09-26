import os

raw_dir = 'data/raw'

# Mapeo de nombres actuales a nombres en español oficiales
rename_map = {
    'bastiat_the_law.txt': 'La Ley - Frederic Bastiat.txt',
    'locke_tratado_gobierno.txt': 'Segundo Tratado sobre el Gobierno Civil - John Locke.txt',
    'SECOND TREATISE OF GOVERNMENT.txt': None, # None means delete duplicate
    'mill_sobre_la_libertad.txt': 'Sobre la Libertad - John Stuart Mill.txt',
    'On Liberty.txt': None, # Delete duplicate
    'smith_riqueza_naciones.txt': 'La Riqueza de las Naciones - Adam Smith.txt',
    'Wealth of nations.txt': None, # Delete duplicate
    'spooner_no_treason.txt': 'Sin Traición - Lysander Spooner.txt',
    'Principles of Political Economy.txt': 'Principios de Economia Politica - David Ricardo.txt',
    'THE THEORY OF MORAL SENTIMENTS.txt': 'Teoria de los Sentimientos Morales - Adam Smith.txt',
    'An Essay Concerning Humane Understanding, Volume 1.txt': 'Ensayo sobre el entendimiento humano Vol 1 - John Locke.txt',
    'An Essay Concerning Humane Understanding, Volume 2.txt': 'Ensayo sobre el entendimiento humano Vol 2 - John Locke.txt',
    'Socialism.txt': 'El Socialismo - John Stuart Mill.txt',
    'Utilitarianism.txt': 'El Utilitarismo - John Stuart Mill.txt'
}

for old_name, new_name in rename_map.items():
    old_path = os.path.join(raw_dir, old_name)
    if os.path.exists(old_path):
        if new_name is None:
            print(f"Eliminando duplicado: {old_name}")
            os.remove(old_path)
        else:
            new_path = os.path.join(raw_dir, new_name)
            # Si el nuevo archivo ya existe (por alguna ejecución previa), eliminamos el viejo
            if os.path.exists(new_path) and old_path != new_path:
                print(f"El destino {new_name} ya existe. Eliminando {old_name}.")
                os.remove(old_path)
            else:
                print(f"Renombrando: {old_name} -> {new_name}")
                os.rename(old_path, new_path)
