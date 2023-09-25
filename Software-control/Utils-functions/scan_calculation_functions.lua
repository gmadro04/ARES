local Utils ={}
function Imprimir(data)
    for i, value in pairs(data) do
        print("Indice " .. i .. " dato: " .. value)
    end
end

function Sum_ranges(max_range, ranges)
    local list_suma = {}
    local sum_lista = 0
    local indice = #ranges -- Tamaño del vector
    for i = 1, indice do
        if 0.0 < ranges[i] and ranges[i] < max_range then
            list_suma[i] = 1.0
        else
            list_suma[i] = 0.0
        end
        sum_lista = sum_lista + list_suma[i]
    end
    -- print("-----------------------------Probando Sum_ranges list_suma---------------------------------------")
    -- Imprimir(list_suma)
    -- print(sum_lista)
    return sum_lista
end

function Pol2cart(rho, phi)
    local cordenadas = {} -- cordenadas cartesianas
    local x, y
    y = rho * math.sin(phi)
    x = rho * math.cos(phi)
    cordenadas = { x, y }
    --Imprimir(cordenadas)
    return cordenadas
end

--[[Funciones principales del programa]]

function Utils.Potential_field(front_attraction, max_range, max_rotational_velocity, max_translational_velocity, min_range,
                         threshold, sensor_ranges, angles)
    -- Llamado de funciones
    ranges = adjust_ranges(sensor_ranges, min_range, max_range)
    -- print("-------------Adjust Ranges salida en potential field----------------")
    -- Imprimir(ranges)
    -- print("--------------------------------------------------------------------")
    obstacle_free = Is_obstacle_free(max_range, ranges, threshold)
    -- print("-------------Obstacle_free salida en potential field----------------")
    -- print(obstacle_free)
    -- print("--------------------------------------------------------------------")
    --ranges = Linear_rating(ranges, max_range)
    -- print("-------------linear_rating salida en potential field----------------")
    -- Imprimir(ranges1)
    -- print("--------------------------------------------------------------------")
    vector = Calculate_vector_normed(front_attraction, ranges, angles)
    -- print("-------------Calculate_vector_normed salida en potential field----------------")
    -- Imprimir(vector)
    -- print("--------------------------------------------------------------------")
    --direction = create_normed_twist_message(vector, max_translational_velocity, max_rotational_velocity)
    -- print("-------------created normed twist message salida en potential field----------------")
    -- Imprimir(direction)
    -- print("--------------------------------------------------------------------")
    direction = vector

    return direction, obstacle_free
end

function adjust_ranges(ranges, min_range, max_range)
    local ranges_1 = {}
    local ranges_2 = {}
    for k, value in pairs(ranges) do
        if value > max_range then
            ranges_1[k] = max_range
        else
            ranges_1[k] = value
        end
        -- print("Indice " .. k .. " dato: " .. ranges_1[k])
    end
    -- print("-----------------------------------------------------")
    for k, value in pairs(ranges_1) do
        if value < min_range then
            ranges_2[k] = 0.0
        else
            ranges_2[k] = value
        end
        -- print("Indice " .. k .. " dato: " .. ranges_2[k])
    end
    ranges = ranges_2
    return ranges
end

function Is_obstacle_free(max_range, ranges, threshold)
    local obstacle_free
    ranges = ranges
    max_range = max_range
    sum = Sum_ranges(max_range, ranges) -- aquí mismo hago la funcion sum_ranges
    if sum <= threshold then
        obstacle_free = true          -- verdader 1
    else
        obstacle_free = false         -- falso 0
    end
    return obstacle_free
end

function Linear_rating(ranges, max_range)
    local linear_rating = {}
    for i, value in pairs(ranges) do
        linear_rating[i] = (1 - (value / max_range))
    end
    -- print("---------- Probando la funcion linear_rating-------------")
    -- Imprimir(linear_rating)
    return linear_rating
end

function Calculate_vector_normed(front_attraction, ranges1, angles)
    local vectors, vector
    vectors = calculate_vectors_from_normed_ranges(ranges1, angles)
    vector = combine_vectors(vectors)
    --Imprimir(vector)
    --vector = flip_vector(vector)
    --Imprimir(vector)
    --vector = add_attraction(vector, front_attraction)
    return vector
end

function calculate_vectors_from_normed_ranges(ranges1, angles)
    local result_ranges = {}
    local cordenadas = {}
    for k, data in pairs(ranges1) do
        if data < 1.0 then
            result_ranges = Pol2cart(data, angles[k])
        end
        -- Imprimir(result_ranges)
        cordenadas[k] = {}
        cordenadas[k][1] = result_ranges[1]
        cordenadas[k][2] = result_ranges[2]
        -- Cordenadas guarda en un matriz las componentes x y y calculadas y se retorna a vectors
        -- Si las cordenadas son un valur nil, es decir vacio hay que asignarles el valor de 0.0
        -- para continuar operando, en python no hay prblemas con las listas vacias, en lua si hay
        -- conflicto con operar un valor nulo con uno real 
        if cordenadas[k][1]== nil then
            cordenadas[k][1] = 0.0
        end
        if cordenadas[k][2]== nil then
            cordenadas[k][2] = 0.0
        end
    end
    return cordenadas
end

function combine_vectors(vectors)
    -- Combine the vectors to a single one by summing them up
    local vector = { 0, 0 }
    local indice = #vectors -- Tamaño de la matriz
    -- print("Tamaño matriz vectors ".. indice)
    -- se suman las componentes x y y del arreglo matricial vectors
    for i = 1, indice do
        vector[1] = vector[1] + vectors[i][1]
        vector[2] = vector[2] + vectors[i][2]
    end
    -- print("------------- combine_vectors prueba----------------")
    -- Imprimir(vector)
    --print("----------------------------------------------------")
    return vector
end

function flip_vector(vector)
    -- Flip the direction of the given vector
    local flip = {}
    local indice = #vector
    for i = 1, indice do
        flip[i] = -1 * vector[i]
    end
    --Imprimir(flip)
    return flip
end

function add_attraction(vector, attraction)
    -- Add the given attraction to give vector
    -- This atracction only affects the linear part
    vector[1] = vector[1] + attraction
    -- Imprimir(vector)
    return vector
end

function create_normed_twist_message(vector, max_translational_velocity, max_rotational_velocity)
    -- [[ Create a normed Twist message.
    -- Norm the given vector to not exceed the given max translational velocity and
    -- the rotational velocity of the robot. ]]
    local direction = { 0, 0 } -- primera pos vel linear 2 pos vel anular
    local indice = #vector
    local a = math.sqrt(vector[1] * vector[1] + vector[2] * vector[2])
    for i = 1, indice do
        vector[i] = vector[i] / (math.sqrt(vector[1] * vector[1] + vector[2] * vector[2]))
    end
    direction[1] = max_translational_velocity * vector[1]
    direction[2] = max_rotational_velocity * math.asin(vector[2] / a)
    --Imprimir(direction)
    return direction
end

return Utils