import pandas as pd 
import matplotlib.pyplot as plt
"""
PROCESAMIENTO DE LOS DATOS DE LOS EXPERIMENTOS
"""
# Cargar el archivo CSV con los datos de la simulación
df = pd.read_csv('Experimentos/datos.csv')

# Ordenar los datos por el número de robots
df.sort_values(by=['NumRobots'], inplace=True)


# Iterar sobre experimentos y calcular la escalabilidad
escalabilidad = []
deltaP = 0
deltaN = 0
escalabilidad.append(0)
for i in range(len(df)-1):
    deltaP = (df['Performance'][i+1] - df['Performance'][i]) / df['Performance'][i]
    deltaN = (df['NumRobots'][i+1] - df['NumRobots'][i]) / df['NumRobots'][i]
    M_S = deltaP/deltaN
    escalabilidad.append(M_S)

# Agregar la lista de escalabilidad al DataFrame
df['Scalability'] = escalabilidad

# Imprimir o mostrar los resultados
print(df[['Experimento', 'MisionID', 'Arenatype', 'Arenatam', 'NumRobots', 'Time', 'Performance', 'Scalability']])
#print(escalabilidad)

#GRAFICAS 
# Graficar los resultados
plt.bar(df['NumRobots'],df['Scalability'])
plt.ylabel('Scalability')
plt.xlabel('Incremento de Robots (N+m)')
plt.title('Escalabilidad vs Incremento de Robots')
plt.show()



