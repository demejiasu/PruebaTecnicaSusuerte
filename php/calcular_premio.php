<?php

/**
 * Calcula el premio acumulado recorriendo recursivamente un arbol de niveles.
 *
 * Cada nodo del arbol tiene la siguiente estructura:
 *   ['monto' => float, 'hijos' => [nodo, nodo, ...]]
 *
 * La funcion suma el monto del nodo actual y el de todos sus hijos
 * de forma recursiva, sin usar bucles.
 *
 * @param array $niveles Arbol de premios anidados.
 * @return float Suma total de todos los montos en el arbol.
 */
function calcularPremioAcumulado(array $niveles): float
{
    // Caso base: si el arreglo esta vacio, retorna 0
    if (empty($niveles)) {
        return 0.0;
    }

    // Procesar el primer elemento del arreglo
    $nodo = array_shift($niveles);
    $monto = $nodo['monto'];
    $hijos = $nodo['hijos'] ?? [];

    // Sumar recursivamente: monto del nodo + premio de sus hijos
    // + premio de los nodos restantes en el mismo nivel
    return $monto + calcularPremioAcumulado($hijos) + calcularPremioAcumulado($niveles);
}

// --- Ejemplo de uso ---

$niveles = [
    [
        'monto' => 1000,
        'hijos' => [
            [
                'monto' => 500,
                'hijos' => []
            ],
            [
                'monto' => 250,
                'hijos' => [
                    [
                        'monto' => 100,
                        'hijos' => []
                    ]
                ]
            ]
        ]
    ]
];

$resultado = calcularPremioAcumulado($niveles);
echo "Premio acumulado: " . $resultado . "\n";
// Resultado esperado: 1850