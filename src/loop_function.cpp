
#include "loop_function.h"
#include <fstream>  // Para trabajar con archivos de salida
#include <argos3/core/utility/math/rng.h>
#include <cmath>
#include <numeric>




/****************************************/
/****************************************/

static const Real AREA_ARENA =   80.0f;

Real m_fLengthSide = Sqrt(AREA_ARENA);
Real m_fHypotenus = m_fLengthSide/2;
Real m_fPosMiddle = Sqrt(Square(m_fHypotenus)/2);

static const Real RADIUS_NEST         = 1.5f;
static const Real RADIUS_SOURCE         = 1.0f;

static const Real SPAWN_SIDE_LENGTH     = 3.0f;

static const Real NEST_MINX            = -1.85f;
static const Real NEST_MAXX            = 1.85f;
static const Real NEST_MINY            = -7.0f;
static const Real NEST_MAXY            = -5.3f;

static const Real FORB_A_MINY            = -1.0f;
static const Real FORB_A_MAXY            = -0.50f;
static const Real FORB_A_MAXX            =  2.5f;

static const Real FORB_B_MINY            = -3.25;
static const Real FORB_B_MAXY            = -2.75;
static const Real FORB_B_MINX            = -1.0f;

static const Real HEIGHT_WALLS         = 0.15f;
static const Real WIDTH_WALLS         = 0.05f;



#define PI 3.14159265


/****************************************/
/****************************************/

CForaging::CForaging() {
  m_unNbrItemsCollected = 0;
  m_unTimeStep = 0;
  for (size_t i = 0; i < NUM_ROBOTS; ++i) {
    m_sFoodData[i] = 0;
  }
}

/****************************************/
/****************************************/

CForaging::~CForaging() {
}

/****************************************/
/****************************************/

void CForaging::Init(TConfigurationNode& t_tree) {
    /* Get output file name from XML tree */
    GetNodeAttribute(t_tree, "output", m_strOutFile);


    TConfigurationNode cParametersNode;
    TConfigurationNode cDistributeNode;
    try
    {
      // Lee el atributo 'atributo' y almacénalo en una variable
      cParametersNode = GetNode(t_tree,"params");
      GetNodeAttributeOrDefault(cParametersNode,"num_experiment",m_unExperiment,m_unExperiment);
      GetNodeAttributeOrDefault(cParametersNode, "arena", m_unArenatype, m_unArenatype);
      GetNodeAttributeOrDefault(cParametersNode, "tam", m_unArenatam, m_unArenatam);
      GetNodeAttributeOrDefault(cParametersNode, "mision", m_unIDmision, m_unIDmision);
      GetNodeAttributeOrDefault(cParametersNode, "obstaculos", m_unObsbool, m_unObsbool);
      GetNodeAttributeOrDefault(cParametersNode, "num_circles", m_unNumCircles, m_unNumCircles);
      GetNodeAttributeOrDefault(cParametersNode, "robots", m_unRobots, m_unRobots);
    }
    catch(const std::exception& e)
    {
      LOGERR << "Problem with Attributes in node params" << std::endl;
    }
    // Variables para el uso de las metricas de evaluación seun la misión
    // --- Exploración ---
    m_arenaSize = 0.0; // se ajusta segun la arena
    if (m_unArenatype == "Octagonal" || m_unArenatype == "Dodecagono")
    {
      m_gridSize = 10;
    }
    else
    {
      m_gridSize = Asignar_tamano_segun_arena(m_unArenatam);
    }
    m_grid.assign(m_gridSize, std::vector<int>(m_gridSize, 0));
    // -- Variable funcion objetivo
    m_fObjectiveFunction = 0; // Función objetivo que mide el rendimiento de la mision

    Init();

    /* Arena init*/
    //PositionArena();
}

void CForaging::Init() {
  /* Open the file for text writing */
  m_cOutFile.open(m_strOutFile.c_str(), std::ofstream::out | std::ofstream::trunc);
  if(m_cOutFile.fail()) {
     THROW_ARGOSEXCEPTION("Error opening file \"" << m_strOutFile << "\": " << ::strerror(errno));
  }

  m_pcRNG = CRandom::CreateRNG("argos");

  /* Random position for the source*/
  CRange<Real> cRangeX(-Sqrt(2*Square(m_fLengthSide))/2, Sqrt(2*Square(m_fLengthSide))/2);
  CRange<Real> cRangeY(0, m_fPosMiddle);
  bool bDone = false;
  do {
    m_cCoordSource = CVector2(m_pcRNG->Uniform(cRangeX), m_pcRNG->Uniform(cRangeY));

    CVector2 cLeftCorner(-Sqrt(2*Square(m_fLengthSide))/2, 0);
    CVector2 cTopLeftCorner(-m_fPosMiddle, m_fPosMiddle);
    CVector2 cOutsideLeftCorner(-Sqrt(2*Square(m_fLengthSide))/2, m_fPosMiddle);
    CVector2 cRightCorner(Sqrt(2*Square(m_fLengthSide))/2, 0);
    CVector2 cTopRightCorner(m_fPosMiddle, m_fPosMiddle);
    CVector2 cOutsideRightCorner(Sqrt(2*Square(m_fLengthSide))/2, m_fPosMiddle);

    if (!(IsWithinTriangle(m_cCoordSource, cLeftCorner, cTopLeftCorner, cOutsideLeftCorner) ||
          IsWithinTriangle(m_cCoordSource, cRightCorner, cTopRightCorner, cOutsideRightCorner))) {
      bDone = true;
    }
  }
  while(!bDone);

  /* Position of the nest */
  m_cCoordNest = CVector2(0, -m_fPosMiddle*2);
  m_unNbrItemsCollected = 0;

  /* Position of the light source */

  CSpace::TMapPerType& m_cLight = GetSpace().GetEntitiesByType("light");
  for(CSpace::TMapPerType::iterator it = m_cLight.begin(); it != m_cLight.end(); ++it) {
     /* Get handle to foot-bot entity and controller */
     CLightEntity& cLight = *any_cast<CLightEntity*>(it->second);
     /* Set the position of the light source over the food source*/
     cLight.SetPosition(CVector3(m_cCoordSource.GetX(),m_cCoordSource.GetY(),0.5));
  }

  /* Write the header of the output file */
  m_cOutFile << "#Clock\tItemsCollected" << std::endl;

  // Inicializar las posiciones de los círculos
  ComputeCirclePositions(m_unNumCircles);
  // Posicionar elementos y robots en la arena 
  if (m_unArenatype == "Triangular" || m_unArenatype == "Dodecagono")
  // m_unArenatype == "Octagonal" || m_unArenatype == "Dodecagono"
  {
    //ComputePositionselements();
    MoveRobots();
  }
  InitRobotStates();

}

/****************************************/
/****************************************/

void CForaging::Reset() {

    /* Close the output file */
    m_cOutFile.close();
    if(m_cOutFile.fail()) {
        THROW_ARGOSEXCEPTION("Error closing file \"" << m_strOutFile << "\": " << ::strerror(errno));
    }

    Init();
    MoveRobots();
    m_fObjectiveFunction = 0;
    m_tRobotStates.clear();
    InitRobotStates();

    /* Reseting the variables. */
    for (size_t i = 0; i < NUM_ROBOTS; ++i) {
      m_sFoodData[i] = 0;
    }
    m_unNbrItemsCollected = 0;
    m_unTimeStep = 0;


    /* Errasing content of file. Writting new header. */
    m_cOutFile << "#Clock\tItems" << std::endl;
}

/****************************************/
/****************************************/

void CForaging::Destroy() {
    /* Close the output file */
    m_cOutFile.close();
    if(m_cOutFile.fail()) {
        THROW_ARGOSEXCEPTION("Error closing file \"" << m_strOutFile << "\": " << ::strerror(errno));
    }
}

/****************************************/
/****************************************/

void CForaging::PreStep() {

}

/****************************************/
/****************************************/
//
void CForaging::PostStep() {
  // LLAMADO A LA METRICA SEGUN LA MISION
  ScoreControl();
}
void CForaging::ScoreControl(){
  if (m_unIDmision == 1)
  {
    //LOGERR << "ID MISION 1" << std::endl;
    m_fObjectiveFunction = GetExplorationScore();
  }
  else if (m_unIDmision == 2)
  {
    m_fObjectiveFunction = GetAggregationScore() ;
  }
  else if (m_unIDmision == 3)
  {
    LOGERR << "ID MISION 3" << std::endl;
  }
  else if (m_unIDmision == 4)
  {
    LOGERR << "ID MISION 4" << std::endl;
  }
  else if (m_unIDmision == 5)
  {
    LOGERR << "ID MISION 5" << std::endl;
  }
}

/****************************************/
/****************************************/

void CForaging::PostExperiment() {
  if (m_unIDmision == 1)
  {
    m_fObjectiveFunction = m_fObjectiveFunction / m_gridSize / m_gridSize;
    LOG << "Exploration Score = " << m_fObjectiveFunction << std::endl;
  }
  else if (m_unIDmision == 2)
  {
    m_fObjectiveFunction = GetAggregationScore();
    LOG << "Agregación Score = " << m_fObjectiveFunction << std::endl;
  }
  else if (m_unIDmision == 3)
  {
    LOGERR << "ID MISION 3" << std::endl;
  }
  else if (m_unIDmision == 4)
  {
    LOGERR << "ID MISION 4" << std::endl;
  }
  else if (m_unIDmision == 5)
  {
    LOGERR << "ID MISION 5" << std::endl;
  }
  // Llama a la función para guardar las posiciones finales de los robots
  SaveRobotPositions();
  SaveExperimentData();
}

void CForaging::SaveRobotPositions() {
  // Crear y abrir un archivo de texto
  //std::ofstream MyFile("posiciones.txt", std::ios_base::trunc);
  std::ofstream MyFile("Experimentos/posiciones.txt", std::ios_base::app);

  CSpace::TMapPerType& tFootBotMap = GetSpace().GetEntitiesByType("foot-bot");
  CVector2 cFootBotPosition(0, 0);

  // Escribir el número de simulación en el archivo
        // Escribir el número de simulación y encabezado en el archivo
        MyFile << "Experimento: " << m_unExperiment << std::endl;
        MyFile << "Posiciones robots:" << std::endl;

        for (CSpace::TMapPerType::iterator it = tFootBotMap.begin(); it != tFootBotMap.end(); ++it) {
            CFootBotEntity* pcFootBot = any_cast<CFootBotEntity*>(it->second);
            std::string strRobotId = pcFootBot->GetId();
            cFootBotPosition.Set(pcFootBot->GetEmbodiedEntity().GetOriginAnchor().Position.GetX(),
                pcFootBot->GetEmbodiedEntity().GetOriginAnchor().Position.GetY());

            // Escribir en el archivo
            MyFile << "[" << strRobotId << ", " << cFootBotPosition << "]" << std::endl;
            //LOG << cFootBotPosition << std::endl;
        }
        // Cerrar el archivo
        MyFile.close();

}

void CForaging::SaveExperimentData() {
  std::ofstream MyFile("Experimentos/datos.csv", std::ios_base::app);
  // Escribir encabezados si el archivo está vacío
  if (MyFile.tellp() == 0) {
      MyFile << "Experiment,MisionID,Mision,Arenatype,Arenasize,NumRobots,Time,Performance" << std::endl;
  }
  std::string Mision;
  if (m_unIDmision == 1)
  {
    Mision = "Exploration";
  }
  else if (m_unIDmision == 2)
  {
    Mision = "Aggregation";
  }
  else if (m_unIDmision == 3)
  {
    Mision = "Pattern formation";
  }
  else if (m_unIDmision == 4)
  {
    Mision = "Synchronization";
  }
  else{
    Mision = "Color selection";
  }

  // Escribir datos en formato CSV con cada valor en una celda separada
  MyFile << m_unExperiment << ",";
  MyFile << m_unIDmision << ",";
  MyFile << Mision << ",";
  MyFile << m_unArenatype << ",";
  MyFile << m_unArenatam << ",";
  MyFile << m_unRobots << ",";
  MyFile << "240 Seg" << ",";
  MyFile << m_fObjectiveFunction << std::endl;
  // Cerrar el archivo
  MyFile.close();
}


/****************************************/
/****************************************/

CColor CForaging::GetFloorColor(const CVector2& c_position_on_plane) {
    /* Nest area is black. */ 
    CVector2 vCurrentPoint(c_position_on_plane.GetX(), c_position_on_plane.GetY());
    Real d = (m_cCoordNest - vCurrentPoint).Length();

    CVector2 vCoordTrianglePointLeft = CVector2(m_cCoordNest.GetX()+RADIUS_NEST, m_cCoordNest.GetY()+RADIUS_NEST);
    CVector2 vCoordTrianglePointRight = CVector2(m_cCoordNest.GetX()-RADIUS_NEST, m_cCoordNest.GetY()+RADIUS_NEST);

  //  if ((d <= RADIUS_NEST) && (IsWithinTriangle(vCurrentPoint, m_cCoordNest, vCoordTrianglePointLeft, vCoordTrianglePointRight))) {
  //    return CColor::WHITE;
  //  }
//
  //  d = (m_cCoordSource - vCurrentPoint).Length();
//
  //  CVector2 cCenter(0,0);
  //  CVector2 cLeftCorner(-Sqrt(2*Square(m_fLengthSide))/2, 0);
  //  CVector2 cRightCorner(Sqrt(2*Square(m_fLengthSide))/2, 0);
  //  CVector2 cTopLeftCorner(-m_fPosMiddle, m_fPosMiddle);
  //  CVector2 cTopRightCorner(m_fPosMiddle, m_fPosMiddle);
  //  if (d <= RADIUS_SOURCE) {
  //    if (IsWithinTriangle(vCurrentPoint, cCenter, cLeftCorner, cTopLeftCorner) ||
  //          IsWithinTriangle(vCurrentPoint, cCenter, cTopLeftCorner, cTopRightCorner) ||
  //          IsWithinTriangle(vCurrentPoint, cCenter, cTopRightCorner, cRightCorner) ||
  //          (vCurrentPoint.GetY() < 0.0f)) {
  //            return CColor::GRAY60;
  //          }
  //  }


  for (const CVector2& cCirclePos : m_vCirclePositions) {
      Real fCircleRadius = RADIUS_SOURCE;  // Ajusta el radio del círculo según tus necesidades

      // Convertir CVector2 a std::pair<double, double>
      std::pair<double, double> point_as_pair(cCirclePos.GetX(), cCirclePos.GetY());

      if ((cCirclePos - c_position_on_plane).Length() <= fCircleRadius) {
        return CColor::BLACK;
      }
  }
    /* Rest of the arena is gray. */
    return CColor::GRAY60;
}
/****************************************/
/****************************************/
/*CONFIGURACION POSICIONES ZONAS Y OBJETOS*/

void CForaging::ComputeCirclePositions(UInt32 NumCircles) {
    double tam = Asignar_tamano_segun_arena(m_unArenatam);

    if (tam < 0.0) {
        // Lanza una excepción indicando el error
        THROW_ARGOSEXCEPTION("Error al asignar un tamaño");
    }

    m_vCirclePositions.clear();  // Limpia el vector antes de añadir nuevas posiciones
    if (m_unArenatype == "Triangular"){

      // Almacenar las posiciones dentro del triángulo en un vector
      std::vector<CVector2> puntos_en_el_triangulo;

      // Recorrer puntos en x desde -tam a tam con variación de 0.2
      for (double x = -tam; x <= tam; x += 0.2) {
        // Recorrer puntos en y desde -tam a tam con variaciones de 0.5
        for (double y = -tam; y <= tam; y += 0.5) {
            std::pair<double, double> punto_actual = std::make_pair(x, y);

            // Verificar si el punto está dentro del triángulo
            if (Dentro_del_triangulo(punto_actual, tam)) {
              puntos_en_el_triangulo.push_back(CVector2(punto_actual.first, punto_actual.second));
            }
        }
        // Seleccionar aleatoriamente NumCircles posiciones del vector
        if (puntos_en_el_triangulo.size() < NumCircles) {
            // Si hay menos puntos dentro del triángulo que el número deseado de círculos,
            // simplemente selecciona todos los puntos disponibles
            m_vCirclePositions = puntos_en_el_triangulo;
        } else {
            // Si hay más puntos dentro del triángulo que el número deseado de círculos,
            // selecciona aleatoriamente NumCircles posiciones
            std::random_shuffle(puntos_en_el_triangulo.begin(), puntos_en_el_triangulo.end());
            m_vCirclePositions.assign(puntos_en_el_triangulo.begin(), puntos_en_el_triangulo.begin() + NumCircles);
        }
      }
    }
    else if (m_unArenatype == "Hexagonal" || m_unArenatype == "Octagonal" || m_unArenatype == "Dodecagono"){
      // Almacenar las posiciones dentro del circulo inscrito en los poligonos en un vector
      std::vector<CVector2> puntos_en_el_circulo;

      for (double x = -tam; x <= tam; x += 0.2) {
          for (double y = -tam; y <= tam; y += 0.5) {
              std::pair<double, double> punto_actual = std::make_pair(x, y);
              if (Dentro_del_circulo(punto_actual, tam)) {
                  puntos_en_el_circulo.push_back(CVector2(punto_actual.first, punto_actual.second));
              }
          }
      }
      // Seleccionar aleatoriamente NumCircles posiciones del vector
      if (puntos_en_el_circulo.size() < NumCircles) {
          // Si hay menos puntos dentro del círculo que el número deseado de círculos,
          // simplemente selecciona todos los puntos disponibles
          m_vCirclePositions = puntos_en_el_circulo;
      } else {
          // Si hay más puntos dentro del círculo que el número deseado de círculos,
          // selecciona aleatoriamente NumCircles posiciones
          std::random_shuffle(puntos_en_el_circulo.begin(), puntos_en_el_circulo.end());
          m_vCirclePositions.assign(puntos_en_el_circulo.begin(), puntos_en_el_circulo.begin() + NumCircles);
      }
    }
    else{ // arena cuadrada
      for(size_t i = 0; i < NumCircles; ++i) {
        CRange<Real> cRangeX(-tam/2, tam/2);
        CRange<Real> cRangeY(-tam/2,tam/2);
        m_vCirclePositions.push_back(CVector2(m_pcRNG->Uniform(cRangeX), m_pcRNG->Uniform(cRangeY)));
      }
    }
}

void CForaging::ComputeElementsPositions(UInt32 NumIter) {
    double tam = Asignar_tamano_segun_arena(m_unArenatam);

    if (tam < 0.0) {
        // Lanza una excepción indicando el error
        THROW_ARGOSEXCEPTION("Error al asignar un tamaño");
    }

    m_vElementsPositions.clear();  // Limpia el vector antes de añadir nuevas posiciones
    if (m_unArenatype == "Triangular"){

      // Almacenar las posiciones dentro del triángulo en un vector
      std::vector<CVector2> puntos_en_el_triangulo;

      // Recorrer puntos en x desde -tam a tam con variación de 0.2
      for (double x = -tam; x <= tam; x += 0.2) {
        // Recorrer puntos en y desde -tam a tam con variaciones de 0.5
        for (double y = -tam; y <= tam; y += 0.5) {
            std::pair<double, double> punto_actual = std::make_pair(x, y);

            // Verificar si el punto está dentro del triángulo
            if (Dentro_del_triangulo(punto_actual, tam)) {
              puntos_en_el_triangulo.push_back(CVector2(punto_actual.first, punto_actual.second));
            }
        }
        // Seleccionar aleatoriamente NumCircles posiciones del vector
        if (puntos_en_el_triangulo.size() < NumIter) {
            // Si hay menos puntos dentro del triángulo que el número deseado de círculos,
            // simplemente selecciona todos los puntos disponibles
            m_vElementsPositions = puntos_en_el_triangulo;
        } else {
            // Si hay más puntos dentro del triángulo que el número deseado de círculos,
            // selecciona aleatoriamente NumCircles posiciones
            std::random_shuffle(puntos_en_el_triangulo.begin(), puntos_en_el_triangulo.end());
            m_vElementsPositions.assign(puntos_en_el_triangulo.begin(), puntos_en_el_triangulo.begin() + NumIter);
        }
      }
    }
    else if (m_unArenatype == "Hexagonal" || m_unArenatype == "Octagonal" || m_unArenatype == "Dodecagono"){
      // Almacenar las posiciones dentro del circulo inscrito en los poligonos en un vector
      std::vector<CVector2> puntos_en_el_circulo;

      for (double x = -tam; x <= tam; x += 0.2) {
          for (double y = -tam; y <= tam; y += 0.5) {
              std::pair<double, double> punto_actual = std::make_pair(x, y);
              if (Dentro_del_circulo(punto_actual, tam)) {
                  puntos_en_el_circulo.push_back(CVector2(punto_actual.first, punto_actual.second));
              }
          }
      }
      // Seleccionar aleatoriamente NumCircles posiciones del vector
      if (puntos_en_el_circulo.size() < NumIter) {
          // Si hay menos puntos dentro del círculo que el número deseado de círculos,
          // simplemente selecciona todos los puntos disponibles
          m_vElementsPositions = puntos_en_el_circulo;
      } else {
          // Si hay más puntos dentro del círculo que el número deseado de círculos,
          // selecciona aleatoriamente NumCircles posiciones
          std::random_shuffle(puntos_en_el_circulo.begin(), puntos_en_el_circulo.end());
          m_vElementsPositions.assign(puntos_en_el_circulo.begin(), puntos_en_el_circulo.begin() + NumIter);
      }
    }
    else{ // arena cuadrada
      for(size_t i = 0; i < NumIter; ++i) {
        //m_vCirclePositions.push_back(CVector2(i, 0.0));
        CRange<Real> cRangeX((-tam/2) + 1.0, (tam/2) - 1.0);
        CRange<Real> cRangeY((-tam/2) + 1.0, (tam/2) - 1.0);
        m_vElementsPositions.push_back(CVector2(m_pcRNG->Uniform(cRangeX), m_pcRNG->Uniform(cRangeY)));
      }
    }
}

/****************************************/
/****************************************/
// Configuraciones posiciones en  la arena segun la geometría
// Definir la función para verificar si un punto está dentro del triángulo
bool CForaging::Dentro_del_triangulo(const std::pair<double, double>& punto, double tam) {
    // Definir los vértices del triángulo
    CVector2 A((tam / 2)-0.7, 0);
    CVector2 B((-tam / 2)+0.7, (tam / 2)-0.7);
    CVector2 C((-tam / 2)+0.7, (-tam / 2)+0.7);
    // Implementación de la función que ya proporcionaste
    // ...
    double x = punto.first;
    double y = punto.second;

    double x1 = A.GetX();
    double y1 = A.GetY();
    double x2 = B.GetX();
    double y2 = B.GetY();
    double x3 = C.GetX();
    double y3 = C.GetY();


    double denominador = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3);
    double alpha = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / denominador;
    double beta = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / denominador;
    double gamma = 1 - alpha - beta;

    // Excluir puntos en la frontera
    return 0 < alpha && alpha < 1 && 0 < beta && beta < 1 && 0 < gamma && gamma < 1;
}

// Definir la función para verificar si un punto está dentro de la circunferencia inscrita en los poligonos segun el tamaño

bool CForaging::Dentro_del_circulo(const std::pair<double,double>& punto, double tam){
    // Calcula la distancia desde el punto al centro del círculo
    double radio = (tam / 2) - 0.7;
    double distancia = (CVector2(punto.first, punto.second) - CVector2(0, 0)).Length();

    // Compara la distancia con el radio
    return distancia < radio;
}

// Función para asignar el tamaño según el tipo de arena
double CForaging::Asignar_tamano_segun_arena(const std::string& arena_tipo) {
    if (arena_tipo == "pequena") {
        return 4.0;
    } else if (arena_tipo == "mediana") {
        return 8.0;
    } else if (arena_tipo == "grande") {
        return 12.0;
    } else {
        // Manejar el caso en el que arena_tipo no sea un valor válido
        std::cerr << "Valor no válido para arena_tipo: " << arena_tipo << std::endl;
        return -1.0;  // Otra forma de manejar el error, devolver un valor no válido
    }
}
// Posicionar objetos y robots, si la arena es triangular
void CForaging::ComputePositionselements() {
    CFootBotEntity* pcFootBot;
    CSpace::TMapPerType& tFootBotMap = GetSpace().GetEntitiesByType("foot-bot");
    double tam = Asignar_tamano_segun_arena(m_unArenatam);

    // Almacenar las posiciones dentro del triángulo en un vector
    std::vector<CVector2> pos_triangulo;

    // Recorrer puntos en x desde -tam a tam con variación de 0.1
    for (double x = -tam; x <= tam; x += 0.1) {
        // Recorrer puntos en y desde -tam a tam con variaciones de 0.1
        for (double y = -tam; y <= tam; y += 0.1) {
            std::pair<double, double> punto_actual = std::make_pair(x, y);
            if ( m_unArenatype == "Hexagonal" || m_unArenatype == "Octagonal" || m_unArenatype == "Octagonal" || m_unArenatype == "Dodecagono")
            {
              // Verificar si el punto está dentro de la circunferenciainscrita en el poligono
              if (Dentro_del_circulo(punto_actual, tam)) {
                  pos_triangulo.push_back(CVector2(punto_actual.first, punto_actual.second));
              }
            }
            else{
              // Verificar si el punto está dentro del triángulo
              if (Dentro_del_triangulo(punto_actual, tam)) {
                  pos_triangulo.push_back(CVector2(punto_actual.first, punto_actual.second));
              }
            }
        }
    }

    // Verificar si hay suficientes posiciones precalculadas
    if (pos_triangulo.size() < tFootBotMap.size()) {
        // Calcular nuevas posiciones
        ComputeElementsPositions(tFootBotMap.size());

        // Verificar si todavía no hay suficientes posiciones
        if (m_vElementsPositions.size() < tFootBotMap.size()) {
            THROW_ARGOSEXCEPTION("No hay suficientes posiciones precalculadas para colocar todos los robots");
        }
    }

    size_t i = 0;
    UInt32 unTrials;

    for (CSpace::TMapPerType::iterator it = tFootBotMap.begin(); it != tFootBotMap.end(); ++it) {
        pcFootBot = any_cast<CFootBotEntity*>(it->second);

        // Obtener la posición del vector precalculado
        const CVector2& cPosition = (pos_triangulo.size() >= tFootBotMap.size()) ? pos_triangulo[i] : m_vElementsPositions[i];

        // Mover el robot a la posición
        bool bPlaced = MoveEntity(pcFootBot->GetEmbodiedEntity(),
            CVector3(cPosition.GetX(), cPosition.GetY(), 0.0),
            CQuaternion().FromEulerAngles(m_pcRNG->Uniform(CRange<CRadians>(CRadians::ZERO, CRadians::TWO_PI)),
                CRadians::ZERO, CRadians::ZERO), false);

        // Intentar colocar el robot hasta un máximo de 100 veces
        unTrials = 0;
        while (!bPlaced && unTrials < 100) {
            // Calcular nuevas posiciones
            ComputeElementsPositions(1);

            // Obtener la nueva posición del vector precalculado
            const CVector2& cNewPosition = m_vElementsPositions[0];

            // Mover el robot a la nueva posición
            bPlaced = MoveEntity(pcFootBot->GetEmbodiedEntity(),
                CVector3(cNewPosition.GetX(), cNewPosition.GetY(), 0.0),
                CQuaternion().FromEulerAngles(m_pcRNG->Uniform(CRange<CRadians>(CRadians::ZERO, CRadians::TWO_PI)),
                    CRadians::ZERO, CRadians::ZERO), false);

            ++unTrials;
        }

        // Verificar si todavía no se pudo colocar el robot
        if (!bPlaced) {
            THROW_ARGOSEXCEPTION("No se pudo colocar el robot después de varios intentos");
        }

        // Incrementar el índice para obtener la siguiente posición precalculada
        ++i;
    }
}

/****************************************/
/* METRICAS DE LA MISION
*/
/****************************************/
//---- AGREGACIÓN ----
void CForaging::InitRobotStates() {
  CSpace::TMapPerType& tFootbotMap = GetSpace().GetEntitiesByType("foot-bot");
  CVector2 cFootbotPosition(0, 0);
  for(CSpace::TMapPerType::iterator it = tFootbotMap.begin(); it != tFootbotMap.end(); ++it) {
      /* Get handle to foot-bot entity and controller */
      CFootBotEntity& cFootBot = *any_cast<CFootBotEntity*>(it->second);
      CVector2 cPos;
      cPos.Set(cFootBot.GetEmbodiedEntity().GetOriginAnchor().Position.GetX(), cFootBot.GetEmbodiedEntity().GetOriginAnchor().Position.GetY());
      m_tRobotStates[&cFootBot].cLastPosition = cPos;
      m_tRobotStates[&cFootBot].cPosition = cPos;
      m_tRobotStates[&cFootBot].unItem = 0;
      m_tRobotStates[&cFootBot].FTimeInAgg = 0.0;
  }
}

Real CForaging::GetAggregationScore() {

    UpdateRobotPositions();
    UpdateAggregationTime();
    // Inicializar variables para contadores
    bool bInAgg;
    Real unRobotsInAgg = 0;
    Real fTotalAggTime = 0.0;
    TRobotStateMap::iterator it;
    // Iterar sobre los estados de los robots
    for (it = m_tRobotStates.begin(); it != m_tRobotStates.end(); ++it) {
        // Verificar si el robot está dentro del círculo de agregación
        bInAgg = IsRobotInAggCircle(it->first->GetEmbodiedEntity().GetOriginAnchor().Position.GetX(),
                               it->first->GetEmbodiedEntity().GetOriginAnchor().Position.GetY());
        if (bInAgg) {
            unRobotsInAgg+=1;
            // Si está en la zona, acumular el tiempo que pasa allí
            fTotalAggTime += it->second.FTimeInAgg;
        }
    }
    return unRobotsInAgg;
}

void CForaging::UpdateAggregationTime() {
    TRobotStateMap::iterator it;

    // Iterar sobre los estados de los robots y actualizar el tiempo de agregación
    for (it = m_tRobotStates.begin(); it != m_tRobotStates.end(); ++it) {
        if (IsRobotInAggCircle(it->first->GetEmbodiedEntity().GetOriginAnchor().Position.GetX(),
                               it->first->GetEmbodiedEntity().GetOriginAnchor().Position.GetY())) {
            // Incrementar el tiempo que pasa en la zona
            it->second.FTimeInAgg += GetSpace().GetSimulationClock();
        }
    }
}

void CForaging::UpdateRobotPositions(){
  CSpace::TMapPerType& tFootbotMap = GetSpace().GetEntitiesByType("foot-bot");
  CVector2 cFootbotPosition(0, 0);

  for(CSpace::TMapPerType::iterator it = tFootbotMap.begin(); it != tFootbotMap.end(); ++it) {
      /* Get handle to foot-bot entity and controller */
      CFootBotEntity& cFootBot = *any_cast<CFootBotEntity*>(it->second);
      CVector2 cPos;
      cPos.Set(cFootBot.GetEmbodiedEntity().GetOriginAnchor().Position.GetX(), cFootBot.GetEmbodiedEntity().GetOriginAnchor().Position.GetY());
      m_tRobotStates[&cFootBot].cLastPosition = m_tRobotStates[&cFootBot].cPosition;
      m_tRobotStates[&cFootBot].cPosition = cPos;
  }
}

bool CForaging::IsRobotInAggCircle(Real x, Real y) {
    // Itera sobre las posiciones de los círculos
    for (const CVector2& circlePos : m_vCirclePositions) {
        // Calcula la distancia entre el robot y la posición del círculo actual
        CVector2 robotPos(x, y);
        CVector2 circleCenter(circlePos.GetX(), circlePos.GetY());
        Real distancia = (circleCenter-robotPos).Length();
        Real radio = RADIUS_SOURCE;

        // Verifica si el robot está dentro del círculo
        if (distancia <= radio + 0.1) {
            return true;  // El robot está dentro de al menos un círculo
        }
    }
    // El robot no está dentro de ninguno de los círculos
    return false;
}
// --- EXPLORACION ----
Real CForaging::GetExplorationScore() {
    CSpace::TMapPerType& tFootBotMap = GetSpace().GetEntitiesByType("foot-bot");
    CVector2 cFootBotPosition(0, 0);
    Real Exploration = 0;
    m_arenaSize = Asignar_tamano_segun_arena(m_unArenatam);

    // Actualiza el contador de tiempo para las baldosas cruzadas por robots
    for (CSpace::TMapPerType::iterator it = tFootBotMap.begin(); it != tFootBotMap.end(); ++it) {
        CFootBotEntity* pcFootBot = any_cast<CFootBotEntity*>(it->second);
        cFootBotPosition.Set(pcFootBot->GetEmbodiedEntity().GetOriginAnchor().Position.GetX(),
            pcFootBot->GetEmbodiedEntity().GetOriginAnchor().Position.GetY());

        UInt32 X = (UInt32)m_gridSize * (cFootBotPosition.GetX() / m_arenaSize + 0.5);
        UInt32 Y = (UInt32)m_gridSize * (cFootBotPosition.GetY() / m_arenaSize + 0.5);

        if (X < m_gridSize && Y < m_gridSize && X >= 0 && Y >= 0) {
            m_grid[X][Y] = 0;
        }
    }

    // Calcula la métrica de exploración
    UInt32 total = 0;
    for (UInt32 i = 0; i < m_gridSize; i++) {
        for (UInt32 j = 0; j < m_gridSize; j++) {
            total += m_grid[i][j];
            m_grid[i][j] += 1;
        }
    }
    Exploration += Real(total);
    return Exploration;
}



/****************************************/
/****************************************/

bool CForaging::IsOnForbidden(CVector2& c_position_robot) {

  /*
  if(c_position_robot.GetY()<=FORB_A_MAXY && c_position_robot.GetY()>=FORB_A_MINY){
    if(c_position_robot.GetX()<FORB_A_MAXX)
      return true;
  }
  */

  if(c_position_robot.GetY()<=FORB_B_MAXY && c_position_robot.GetY()>=FORB_B_MINY){
    if(c_position_robot.GetX()>FORB_B_MINX)
      return true;
  }

  return false;
}

/****************************************/
/****************************************/

bool CForaging::IsOnNest(CVector2& c_position_robot) {
  if ((m_cCoordNest - c_position_robot).Length() <= RADIUS_NEST) {
     return true;
  }
  return false;
}

/****************************************/
/****************************************/

bool CForaging::IsOnSource(CVector2& c_position_robot) {
  if ((m_cCoordSource - c_position_robot).Length() <= RADIUS_SOURCE) {
     return true;
  }
  return false;
}

/****************************************/
/****************************************/

bool CForaging::IsWithinTriangle(CVector2& c_point_q, CVector2& c_point_a, CVector2& c_point_b, CVector2& c_point_c) {
  Real fAreaTriangle = AreaTriangle(c_point_a, c_point_b, c_point_c);
  Real fAreaABQ = AreaTriangle(c_point_a, c_point_b, c_point_q);
  Real fAreaBCQ = AreaTriangle(c_point_b, c_point_c, c_point_q);
  Real fAreaACQ = AreaTriangle(c_point_a, c_point_c, c_point_q);

  if (Abs(fAreaTriangle - (fAreaABQ + fAreaACQ + fAreaBCQ)) < 0.0001) {
    return true;
  } else {
    return false;
  }
}

/****************************************/
/****************************************/

Real CForaging::AreaTriangle(CVector2& c_point_a, CVector2& c_point_b, CVector2& c_point_c) {
  Real fArea = Abs(c_point_a.GetX()*(c_point_b.GetY()-c_point_c.GetY()) + c_point_b.GetX()*(c_point_c.GetY()-c_point_a.GetY()) + c_point_c.GetX()*(c_point_a.GetY()-c_point_b.GetY()))/2;
  return fArea;
}

/****************************************/
/****************************************/
void CForaging::PositionArena() {

}

/****************************************/
/****************************************/

void CForaging::MoveRobots() {
  CFootBotEntity* pcFootBot;
  bool bPlaced = false;
  UInt32 unTrials;
  CSpace::TMapPerType& tFootBotMap = GetSpace().GetEntitiesByType("foot-bot");
  for (CSpace::TMapPerType::iterator it = tFootBotMap.begin(); it != tFootBotMap.end(); ++it) {
    pcFootBot = any_cast<CFootBotEntity*>(it->second);
    // Choose position at random
    unTrials = 0;
    do {
       ++unTrials;
       CVector3 cFootBotPosition = GetRandomPosition();
       //cFootBotPosition.GetX();
      bPlaced = MoveEntity(pcFootBot->GetEmbodiedEntity(),
                            cFootBotPosition,
                            CQuaternion().FromEulerAngles(m_pcRNG->Uniform(CRange<CRadians>(CRadians::ZERO,CRadians::TWO_PI)),
                            CRadians::ZERO,CRadians::ZERO),false);
    } while(!bPlaced && unTrials < 200);
    if(!bPlaced) {
       THROW_ARGOSEXCEPTION("Can't place robot");
    }
  }
}

/****************************************/
/****************************************/

CVector3 CForaging::GetRandomPosition() {
  double tam = Asignar_tamano_segun_arena(m_unArenatam);
  Real a = m_pcRNG->Uniform(CRange<Real>(-1.0f, 1.0f));
  Real b = m_pcRNG->Uniform(CRange<Real>(-1.0f, 1.0f));
  Real x;
  Real y;
  //return CVector3(a*SPAWN_SIDE_LENGTH, b*SPAWN_SIDE_LENGTH, 0.0f);

  if (m_unArenatype == "Triangular")
  {
    CVector2 A((tam / 2), 0);
    CVector2 B((-tam / 2), (tam / 2));
    CVector2 C((-tam / 2), (-tam / 2));
    // Ajustar valores de a y b al rango [0, 1]
    a = (a + 1.0) / 2.0;
    b = (b + 1.0) / 2.0;
    // Interpolación para obtener una posición aleatoria dentro del triángulo
    x = (1.0 - std::sqrt(a)) * A.GetX() + std::sqrt(a) * (1.0 - b) * B.GetX() + std::sqrt(a) * b * C.GetX();
    y = (1.0 - std::sqrt(a)) * A.GetY() + std::sqrt(a) * (1.0 - b) * B.GetY() + std::sqrt(a) * b * C.GetY();

  }
  else if (m_unArenatype == "Octagonal") {
    // Definir las coordenadas de los vértices del octágono
    double OctagonRadius = tam / 2;
    std::vector<CVector2> octagonVertices;
    for (UInt32 i = 0; i < 8; ++i) {
      CRadians angle = CRadians::PI_OVER_FOUR * i;

      // Introducir aleatoriedad en las coordenadas de los vértices
      Real randomnessFactor = m_pcRNG->Uniform(CRange<Real>(-1.7f, 1.7f));
      Real m = OctagonRadius * randomnessFactor * std::cos(angle.GetValue());
      Real n = OctagonRadius * randomnessFactor * std::sin(angle.GetValue());

      octagonVertices.emplace_back(m, n);
    }

    a = (a + 1.0) / 2.0;
    b = (b + 1.0) / 2.0;

    // Inicializar posiciones
    x = 0.0;
    y = 0.0;

    // Generar pesos aleatorios
    std::vector<Real> weights;
    for (size_t i = 0; i < octagonVertices.size(); ++i) {
      weights.push_back(m_pcRNG->Uniform(CRange<Real>(0.0, 1.0)));
    }

    // Normalizar pesos para asegurar que sumen 1.0
    Real totalWeight = std::accumulate(weights.begin(), weights.end(), 0.0);
    for (size_t i = 0; i < octagonVertices.size(); ++i) {
      weights[i] /= totalWeight;
    }

    // Aplicar pesos para obtener una posición aleatoria dentro del octágono
    for (size_t i = 0; i < octagonVertices.size(); ++i) {
      x += weights[i] * octagonVertices[i].GetX();
      y += weights[i] * octagonVertices[i].GetY();
    }
  }
  else if (m_unArenatype == "Dodecagono") {
    // Definir las coordenadas de los vértices del dodecágono
    double DodecagonRadius = tam / 2;
    std::vector<CVector2> dodecagonVertices;
    for (UInt32 i = 0; i < 12; ++i) {
      CRadians angle = CRadians::TWO_PI / 12 * i;

      // Introducir aleatoriedad en las coordenadas de los vértices
      Real randomnessFactor = m_pcRNG->Uniform(CRange<Real>(-2.0f, 2.0f));
      Real m = DodecagonRadius * randomnessFactor * std::cos(angle.GetValue());
      Real n = DodecagonRadius * randomnessFactor * std::sin(angle.GetValue());

      dodecagonVertices.emplace_back(m, n);
    }

    a = (a + 1.0) / 2.0;
    b = (b + 1.0) / 2.0;

    // Inicializar posiciones
    x = 0.0;
    y = 0.0;

    // Generar pesos aleatorios
    std::vector<Real> weights;
    for (size_t i = 0; i < dodecagonVertices.size(); ++i) {
      weights.push_back(m_pcRNG->Uniform(CRange<Real>(0.0, 1.0)));
    }

    // Normalizar pesos para asegurar que sumen 1.0
    Real totalWeight = std::accumulate(weights.begin(), weights.end(), 0.0);
    for (size_t i = 0; i < dodecagonVertices.size(); ++i) {
      weights[i] /= totalWeight;
    }

    // Aplicar pesos para obtener una posición aleatoria dentro del dodecágono
    for (size_t i = 0; i < dodecagonVertices.size(); ++i) {
      x += weights[i] * dodecagonVertices[i].GetX();
      y += weights[i] * dodecagonVertices[i].GetY();
    }
  }
  return CVector3(x, y, 0.0);
}


/****************************************/
/****************************************/

CRadians CForaging::ComputeOrientation(CVector2 vec_a, CVector2 vec_b) {
  Real fDistX = Abs(Abs(vec_a.GetX()) - Abs(vec_b.GetX()));
  Real fDistY = Abs(Abs(vec_a.GetY()) - Abs(vec_b.GetY()));
  return ATan2(fDistX, fDistY);
}

/****************************************/
/****************************************/

CVector2 CForaging::ComputeMiddle(CVector2 vec_a, CVector2 vec_b) {
  return CVector2((vec_a.GetX() + vec_b.GetX())/2, (vec_a.GetY() + vec_b.GetY())/2);
}

/****************************************/
/****************************************/

/* Register this loop functions into the ARGoS plugin system */
REGISTER_LOOP_FUNCTIONS(CForaging, "loop_function");
