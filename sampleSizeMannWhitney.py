from statsmodels.stats.power import TTestIndPower

# Parámetros estándar para el cálculo del tamaño muestral
alpha = 0.05  # Nivel de significancia
power = 0.8  # Potencia deseada
effect_sizes = [0.2, 0.5, 0.8]  # Tamaños de efecto estándar: pequeño, mediano, grande

# Instanciamos el cálculo de potencia para una prueba de dos muestras independientes
analysis = TTestIndPower()

# Calculamos el tamaño muestral para cada tamaño de efecto
sample_sizes = {f"Effect size {d}": analysis.solve_power(effect_size=d, alpha=alpha, power=power, alternative='two-sided')
                for d in effect_sizes}

print(sample_sizes)
