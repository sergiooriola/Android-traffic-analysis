from statsmodels.stats.power import TTestIndPower

# Parámetros estándar
alpha = 0.05  # Nivel de significancia
power = 0.80  # Poder estadístico
effect_size = 0.5  # Tamaño del efecto (medio, según la d de Cohen)

# Inicializamos el análisis de poder para el test t independiente
analysis = TTestIndPower()

# Calculamos el tamaño de muestra necesario por grupo
sample_size_per_group = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power, alternative='two-sided')

# Resultado total (dos grupos)
total_sample_size = sample_size_per_group * 2

print(sample_size_per_group, total_sample_size)
