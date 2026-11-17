import os
import pymupdf # PyMuPDF to convert PDF to PNG image
from PIL import Image

# Data structure containing ALL items grouped by subject line, with their exact legend type/color

data = [
    {
        "category": "Movilidad y Accesibilidad",
        "legend": "pgo",
        "color": "#009688", # Teal
        "text_color": "#ffffff",
        "items": [
            "Definir las acciones que afectan a la zona de contacto con los límites del PRUG Anaga",
            "Alumbrado escaso en los espacios públicos por la Ley del Cielo de Canarias",
            "Suroeste circular",
            "Aparcamientos cerca Hospital Residencia",
            "Nuevas vías con ancho suficiente para la movilidad sostenible",
            "Nuevas centralidades en el Suroeste",
            "Ciudad para el peatón, no para el coche",
            "Restringir acceso de coches al centro de SC (franja horaria)",
            "Peatonalización de los centros urbanos",
            "Conexión viaria entre barrios del Suroeste",
            "Restringir aparcamientos en el centro",
            "Carriles Bici",
            "Solución al estrechamiento de carretera de acceso al Parque Rural por San Andrés",
            "Determinar recorridos preferentes que sean accesibles a sillas de ruedas",
            "Carril bici desde El Corte Inglés a Almeyda",
            "Aparcamientos con edificación en altura"
        ]
    },
    {
        "category": "Varios y Desarrollo Sostenible",
        "legend": "pgo",
        "color": "#009688",
        "text_color": "#ffffff",
        "items": [
            "Preservar idiosincrasia de El Tablero",
            "Baja densidad de población en el Suroeste",
            "Evitar el uso homogéneo del centro de la ciudad (se muere por la noche)",
            "Conservar estilo y calidad de vida. Conservar el silencio en el Suroeste",
            "Armonización de viviendas con el paisaje del Suroeste",
            "Viviendas Cohousing senior",
            "Promover complejidad de usos",
            "Poner Consejería de Educación (GobCan) en El Sobradillo",
            "Descentralizar Consejerías de GobCan y llevarlas al Suroeste",
            "Reparto de VPO más equilibrado en el municipio",
            "Ampliar el área administrativa de Santa Cruz hacia el Suroeste",
            "Punto de información o centro de visitantes fuera del Parque Rural",
            "Suprimir unidades de actuación",
            "+ Suelo rústico",
            "Sistemas bio-urbanos: calles orientadas a corrientes de aire para evitar aires acondicionados",
            "\"Seguir siendo un pueblo\" en el Suroeste",
            "Distribución proporcional y equilibrada del desarrollo urbanístico",
            "Creación de un parque agroecológico en el Suroeste",
            "Rehabilitar el paisaje de la Montaña Talavera",
            "Separar industrias molestas del área residencial",
            "+ Suelo de protección agraria",
            "Huertos urbanos",
            "Bosques comestibles",
            "Considerar las posibles inundaciones y avenidas en los nuevos desarrollos"
        ]
    },
    {
        "category": "Espacio Libre Público",
        "legend": "pgo",
        "color": "#009688",
        "text_color": "#ffffff",
        "items": [
            "Complejidad de usos en espacios públicos",
            "Apertura al mar en todo el municipio",
            "Rutas deportivas iluminadas por la noche",
            "Barrancos conectados mediante red de senderos",
            "Uso de barrancos como zonas verdes",
            "Acceso al mar en Acorán",
            "Renaturalización de espacios urbanos",
            "Ejecución de los Espacios Libres previstos",
            "Rutas deportivas segregadas y aisladas del tráfico",
            "No a la privatización del espacio público (terrazas)"
        ]
    },
    {
        "category": "Dotaciones, Equipamientos e Infraestructuras",
        "legend": "pgo",
        "color": "#009688",
        "text_color": "#ffffff",
        "items": [
            "Centros culturales",
            "Dotaciones Socio-Sanitarias",
            "Pequeños intercambiadores modales en el perímetro de los barrios para dejar el coche",
            "Centro de Salud en el Suroeste",
            "Centros de participación cívica",
            "Depuradora en Igueste de San Andrés",
            "Centros Dotacionales Integrales, polivalentes",
            "Centros Ciudadanos y Espacios de Encuentro",
            "Ejecución de dotaciones previstas en Acorán. Evitar ciudad dormitorio",
            "Intercambiador en el Suroeste",
            "Dotaciones y equipamientos inclusivos",
            "Creación de una central de compostaje en el Suroeste",
            "Centros de día para personas mayores",
            "Mercadillo del Agricultor Suroeste",
            "Camping en el entorno de Las Teresitas",
            "+ Parques Públicos"
        ]
    },
    {
        "category": "Patrimonio Cultural",
        "legend": "pgo",
        "color": "#009688",
        "text_color": "#ffffff",
        "items": [
            "Protección del patrimonio etnográfico",
            "Protección de casas tradicionales",
            "Protección de eras, bancales y paseros",
            "Protección del patrimonio vinculado al agua: atarjeas, aljibes",
            "Rehabilitación del Barranco del Muerto",
            "Protección del Barranco de Jagua",
            "Protección del patrimonio industrial: Naves de Telefónica en el Suroeste",
            "Protección del patrimonio arqueológico de Jagua",
            "Protección del Paisaje",
            "Revisar el Catálogo de Protección para ajustarlo a la realidad",
            "Preservación de los estanques de agua para las aves migratorias y la agricultura",
            "Protección del patrimonio inmaterial"
        ]
    },
    {
        "category": "Cuestiones de competencia del Ayuntamiento",
        "legend": "ayto",
        "color": "#0284c7", # Cyan / Blue
        "text_color": "#ffffff",
        "items": [
            "Mejora estaciones de bombeo de agua en Anaga",
            "Red de recogida de pluviales en Anaga",
            "Depuración de aguas en barrios en ladera",
            "Depuradoras biológicas",
            "Gestión del Patrimonio a través de asociaciones locales",
            "Rehabilitación de viviendas vacías VPO",
            "Acceso a internet en Anaga",
            "Baños públicos",
            "Mejora de aceras",
            "Creación de un área o servicio de movilidad en la estructura municipal",
            "Perspectiva de género en las ordenanzas municipales",
            "Reducción de residuos",
            "Seguridad",
            "Mejora de las vías existentes",
            "Mejora del alumbrado público",
            "Promover servicio de taxi compartido",
            "Infraestructuras contra incendios en los espacios libres públicos",
            "Mejorar señalización de tráfico",
            "Accesibilidad a barrios en ladera (funicular o similar)",
            "Plantar más árboles y prohibir su eliminación",
            "Fomentar centros de participación cívica",
            "Acceso a agua de riego a precio asequible",
            "Favorecer el asociacionismo",
            "Sustitución de iluminación tradicional por renovable",
            "Guarderías públicas"
        ]
    },
    {
        "category": "Posibles propuestas al Plan Estratégico Municipal",
        "legend": "plan",
        "color": "#65a30d", # Light green / Olive
        "text_color": "#ffffff",
        "items": [
            "Ahorro Energético",
            "Divulgación del PMUS",
            "Incentivos a la Economía Circular",
            "Movilidad Sostenible",
            "Fomentar el uso de la bicicleta",
            "Desarrollo del proyecto Ecoeje",
            "Apertura de la ciudad al Mar",
            "Incentivos a Productos Km 0",
            "Cambiar comportamientos de las personas a la hora de moverse en la ciudad",
            "Gran pacto ciudadano por la movilidad sostenible",
            "Espacios Rurales y Agricultura",
            "Fomentar el pequeño comercio de proximidad",
            "Ayudas a la Rehabilitación Eficiente de edificios",
            "Hacer atractiva la ciudad para residir y no perder población",
            "17 ODS (Objetivos de Desarrollo Sostenible de la ONU)",
            "Apostar por un parque de vivienda de alquiler",
            "Lucha contra el Cambio Climático",
            "Divulgación del patrimonio material e inmaterial",
            "Indicadores de seguimiento de la actividad urbana",
            "Fomento de las Energías Limpias"
        ]
    },
    {
        "category": "Cuestiones de competencia del Cabildo de Tenerife",
        "legend": "cabildo",
        "color": "#7e22ce", # Purple
        "text_color": "#ffffff",
        "items": [
            "No al trazado del tranvía por Avda. Los Majuelos",
            "Miradores en Anaga",
            "Desarrollo del proyecto Ecoeje",
            "Aceras en TF-180 Vistabella",
            "Apartaderos en carreteras de Anaga",
            "Guagua circular en el Suroeste",
            "Mejora de la frecuencia del transporte público",
            "Transporte público más barato para reducir el tráfico",
            "Gestión PRUG Anaga",
            "No a la Vía Exterior",
            "Transporte público nocturno"
        ]
    }
]

total_items = sum(len(cat['items']) for cat in data)
print(f"Total items transcribed across all categories: {total_items}")