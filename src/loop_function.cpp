
#include "loop_function.h"
#include <fstream>  // Para trabajar con archivos de salida
#include <argos3/core/utility/math/rng.h>



/****************************************/
/****************************************/

static const Real AREA_ARENA =   80.0f;

Real m_fLengthSide = Sqrt(AREA_ARENA);
Real m_fHypotenus = m_fLengthSide/2;
Real m_fPosMiddle = Sqrt(Square(m_fHypotenus)/2);

static const Real RADIUS_NEST         = 1.5f;
static const Real RADIUS_SOURCE         = 0.5f;

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
    try
    {
      // Lee el atributo 'atributo' y almacénalo en una variable
      cParametersNode = GetNode(t_tree,"params");

      GetNodeAttributeOrDefault(cParametersNode,"num_experiment",m_unExperiment,m_unExperiment);
      GetNodeAttributeOrDefault(cParametersNode, "arena", m_unArenatype, m_unArenatype);
      GetNodeAttributeOrDefault(cParametersNode, "tam", m_unArenatam, m_unArenatam);
      //GetNodeAttributeOrDefault(cParametersNode, "mision", m_unIDmision, m_unIDmision);
      //GetNodeAttributeOrDefault(cParametersNode, "circles", m_unCirclebool, m_unCirclebool);
      GetNodeAttributeOrDefault(cParametersNode, "num_circles", m_unNumCircles, m_unNumCircles);

    }
    catch(const std::exception& e)
    {
      LOGERR << "Problem with Attributes in node params" << std::endl;
    }

    Init();

    /* Arena init*/
    //PositionArena();
}

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
    else{
      for(size_t i = 0; i < NumCircles; ++i) {
        //m_vCirclePositions.push_back(CVector2(i, 0.0));
        CRange<Real> cRangeX(-Sqrt(2*Square(m_fLengthSide))/2, Sqrt(2*Square(m_fLengthSide))/2);
        CRange<Real> cRangeY(0, m_fPosMiddle);
        //mCoordSource = CVector2(m_pcRNG->Uniform(cRangeX), m_pcRNG->Uniform(cRangeY));
        //m_vCirclePositions.push_back(CVector2(m_pcRNG->Uniform(CRange<Real>(-4.0f, 4.0f)), m_pcRNG->Uniform(CRange<Real>(-4.0f, 4.0f))));
        m_vCirclePositions.push_back(CVector2(m_pcRNG->Uniform(cRangeX), m_pcRNG->Uniform(cRangeY)));
      }
    }
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

void CForaging::PostStep() {
  UInt32 sCurrentScore = m_unNbrItemsCollected;
  CSpace::TMapPerType& m_cFootbots = GetSpace().GetEntitiesByType("foot-bot");
  UInt8 unRobotId;
  for(CSpace::TMapPerType::iterator it = m_cFootbots.begin(); it != m_cFootbots.end(); ++it) {
     /* Get handle to foot-bot entity and controller */
     CFootBotEntity& cFootBot = *any_cast<CFootBotEntity*>(it->second);
     /* Get the position of the foot-bot on the ground as a CVector2 */
     CVector2 cPos;
     cPos.Set(cFootBot.GetEmbodiedEntity().GetOriginAnchor().Position.GetX(), cFootBot.GetEmbodiedEntity().GetOriginAnchor().Position.GetY());
     unRobotId = atoi(cFootBot.GetId().substr(2, 3).c_str());
     /* If the foot-bot is on the nest, drop the item he is carrying. */
     if (IsOnNest(cPos)) {
       if (m_sFoodData[unRobotId-1] != 0) {
           m_unNbrItemsCollected += 1;
           m_sFoodData[unRobotId-1] = 0;
       }
     } else if (IsOnSource(cPos)) {    /* If the foot-bot is on source, takes corresponding item */
       m_sFoodData[unRobotId-1] = 1;
     } else if (IsOnForbidden(cPos)) {    /* If the foot-bot is on the forbbiden areas, looses corresponding item */
         m_sFoodData[unRobotId-1] = 0;
     }
  }

  /* Increase the time step counter */
  m_unTimeStep += 1;

  /* Writting data to output file. */
  m_cOutFile << m_unTimeStep << "\t" << m_unNbrItemsCollected << std::endl;

  /* Output in simulator */
  if (m_unNbrItemsCollected > sCurrentScore) {
    LOGERR << "Items collected = " << m_unNbrItemsCollected << std::endl;
  }
}


/****************************************/
/****************************************/

void CForaging::PostExperiment() {
    LOG << "Items collected = " << m_unNbrItemsCollected << std::endl;

    // Llama a la función para guardar las posiciones finales de los robots
    SaveRobotPositions();
    SaveExperimentData();

}

void CForaging::SaveRobotPositions() {
  // Crear y abrir un archivo de texto
  //std::ofstream MyFile("posiciones.txt", std::ios_base::trunc);
  std::ofstream MyFile("posiciones.txt", std::ios_base::app);

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
            LOG << cFootBotPosition << std::endl;
        }

        // Cerrar el archivo
        MyFile.close();

}

void CForaging::SaveExperimentData() {
    // Abrir el archivo de texto en modo de adición
    std::ofstream MyFile("datos.txt", std::ios_base::app);
    // Obtener parámetros y métricas desde la configuración
    //std::string strTipoComportamiento, strArena;
    //GetNodeAttributeOrDefault(GetNode(t_tree, "params"), "tipo_comportamiento", strTipoComportamiento, "");
    //GetNodeAttributeOrDefault(GetNode(t_tree, "params"), "arena", strArena, "");
    //UInt32 unTamanoArena, unNumRobots, unTiempoEjecucion;
    //GetNodeAttributeOrDefault(GetNode(t_tree, "params"), "tamano_arena", unTamanoArena, 0);
    //GetNodeAttributeOrDefault(GetNode(t_tree, "params"), "num_robots", unNumRobots, 0);
    //GetNodeAttributeOrDefault(GetNode(t_tree, "params"), "tiempo_ejecucion", unTiempoEjecucion, 0)
    // Obtener métricas de la simulación
    //Real fEvaluacionMision, fEscalabilidad, fFlexibilidad, fToleranciaFallos;
    // ... lógica para obtener las métrica
    // Escribir los datos en el archivo
    MyFile << "----------Experimento:---------- " << std::endl;
    MyFile << "Numero de simulacion: " << m_unExperiment << std::endl;
    MyFile << "----------Parametros:----------" << std::endl;
    MyFile << "Tipo comportamiento: " << "agregación" << std::endl;
    MyFile << "Arena: " << "Octagonal" << std::endl;
    MyFile << "Tamano arena: " << "Mediana" << std::endl;
    MyFile << "Num Robots: " << "20" << std::endl;
    MyFile << "Tiempo ejecucion: " << "1:20m" << std::endl;
    MyFile << "----------Metrica M:----------" << std::endl;
    MyFile << "Evaluacion mision: " << "Score agragación" << std::endl;
    MyFile << "----------Metrica P:----------" << std::endl;
    MyFile << "Escalabilidad: " << "30" << std::endl;
    MyFile << "Flexibilidad: " << "15" << std::endl;
    MyFile << "Tolerancia a fallos: " << "8" << std::endl;
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

    if ((d <= RADIUS_NEST) && (IsWithinTriangle(vCurrentPoint, m_cCoordNest, vCoordTrianglePointLeft, vCoordTrianglePointRight))) {
      return CColor::WHITE;
    }

    d = (m_cCoordSource - vCurrentPoint).Length();

    CVector2 cCenter(0,0);
    CVector2 cLeftCorner(-Sqrt(2*Square(m_fLengthSide))/2, 0);
    CVector2 cRightCorner(Sqrt(2*Square(m_fLengthSide))/2, 0);
    CVector2 cTopLeftCorner(-m_fPosMiddle, m_fPosMiddle);
    CVector2 cTopRightCorner(m_fPosMiddle, m_fPosMiddle);
    if (d <= RADIUS_SOURCE) {
      if (IsWithinTriangle(vCurrentPoint, cCenter, cLeftCorner, cTopLeftCorner) ||
            IsWithinTriangle(vCurrentPoint, cCenter, cTopLeftCorner, cTopRightCorner) ||
            IsWithinTriangle(vCurrentPoint, cCenter, cTopRightCorner, cRightCorner) ||
            (vCurrentPoint.GetY() < 0.0f)) {
              return CColor::BLACK;
            }
    }

    double tam = Asignar_tamano_segun_arena(m_unArenatam);
    /* Long dropping area. FORB A */
    /*
    CVector2 cBottomCornerA(-(1.7*m_fPosMiddle), FORB_A_MINY);
    CVector2 cTLCornerA(-(1.7*m_fPosMiddle), FORB_A_MAXY);
    CVector2 cTRCornerA(-(1.7*m_fPosMiddle)-0.5,FORB_A_MAXY);
    if(vCurrentPoint.GetY()<=FORB_A_MAXY && vCurrentPoint.GetY()>=FORB_A_MINY){
        if(vCurrentPoint.GetX()<FORB_A_MAXX && vCurrentPoint.GetX()>-(1.7*m_fPosMiddle))
            return CColor::GRAY40;
        if (IsWithinTriangle(vCurrentPoint,cBottomCornerA,cTLCornerA,cTRCornerA))
            return CColor::GRAY40;
     }
     */

    /* Short dropping area. FORB B */
    /*CVector2 cBottomCornerB(m_fPosMiddle-0.1, FORB_B_MINY);
    CVector2 cTLCornerB(m_fPosMiddle-0.1, FORB_B_MAXY);
    CVector2 cTRCornerB(m_fPosMiddle+0.4,FORB_B_MAXY);
    if(vCurrentPoint.GetY()<=FORB_B_MAXY && vCurrentPoint.GetY()>=FORB_B_MINY){
        if(vCurrentPoint.GetX()>FORB_B_MINX  && vCurrentPoint.GetX()<m_fPosMiddle-0.1)
            return CColor::GRAY20;
        if (IsWithinTriangle(vCurrentPoint,cBottomCornerB,cTLCornerB,cTRCornerB))
            return CColor::GRAY20;
    }*/
  /*Circulos en la arena según una posición*/
  //for (const CVector2& cCirclePos : m_vCirclePositions) {
  //      Real fCircleRadius = 0.5;  // Ajusta el radio del círculo según tus necesidades
  //      //Se puede remplazar esta vaiable por RADIUS SOURCE
  //      //CVector2 circle_pos = m_vCirclePositions
  //      CVector2 circle_pos =  circle_pos;
  //      if ((cCirclePos - c_position_on_plane).Length() <= fCircleRadius) {
  //          // La posición está dentro del círculo, píntalo de un color específico (por ejemplo, rojo)
  //          //return CColor::BLACK;
  //          if (IsWithinTriangle(circle_pos, cCenter, cLeftCorner, cTopLeftCorner) ||
  //            IsWithinTriangle(circle_pos, cCenter, cTopLeftCorner, cTopRightCorner) ||
  //            IsWithinTriangle(circle_pos, cCenter, cTopRightCorner, cRightCorner) ||
  //            (vCurrentPoint.GetY() < 0.0f)) {
  //            return CColor::BLACK;
  //          }
  //      }
  //}

  for (const CVector2& cCirclePos : m_vCirclePositions) {
      Real fCircleRadius = 0.5;  // Ajusta el radio del círculo según tus necesidades

      // Convertir CVector2 a std::pair<double, double>
      std::pair<double, double> point_as_pair(cCirclePos.GetX(), cCirclePos.GetY());

      if ((cCirclePos - c_position_on_plane).Length() <= fCircleRadius) {
          // La posición está dentro del círculo

          // Verificar si está dentro del triángulo
          bool dentro_del_triangulo = Dentro_del_triangulo(point_as_pair, tam);

          // Verificar si está dentro del área permitida
          bool dentro_del_area_permitida = (vCurrentPoint.GetY() < 0.0f);

          // Pintar de negro solo si está dentro del triángulo
          if (dentro_del_triangulo || dentro_del_area_permitida) {
              return CColor::BLACK;
          } else {
              // Pintar de gris si no está dentro del triángulo
              return CColor::GRAY50;
          }
      }
  }


    /* Rest of the arena is gray. */
    return CColor::GRAY60;
}

/****************************************/
/****************************************/
// COnfiguraciones arena para posiciones 
// Definir la función para verificar si un punto está dentro del triángulo
bool CForaging::Dentro_del_triangulo(const std::pair<double, double>& punto, double tam) {
    // Definir los vértices del triángulo
    CVector2 A(tam / 2, 0);
    CVector2 B(-tam / 2, tam / 2);
    CVector2 C(-tam / 2, -tam / 2);
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

/****************************************/
/****************************************/

void CForaging::PositionArena() {
  
  //CBoxEntity* pcWall;
  //CQuaternion cAngleWall;
//
  //cAngleWall.FromEulerAngles(CRadians::PI_OVER_FOUR, CRadians::ZERO, CRadians::ZERO);
  //pcWall = new CBoxEntity("wall_south_west",
  //    CVector3(-m_fPosMiddle, -m_fPosMiddle, 0.0), // Position
  //    cAngleWall,
  //    false,
  //    CVector3(WIDTH_WALLS, m_fLengthSide, HEIGHT_WALLS));   // Size
  //AddEntity(*pcWall);
//
  //cAngleWall.FromEulerAngles(-CRadians::PI_OVER_FOUR, CRadians::ZERO, CRadians::ZERO);
  //pcWall = new CBoxEntity("wall_south_east",
  //    CVector3(m_fPosMiddle, -m_fPosMiddle, 0.0), // Position
  //    cAngleWall,
  //    false,
  //    CVector3(WIDTH_WALLS, m_fLengthSide, HEIGHT_WALLS));   // Size
  //AddEntity(*pcWall);
//
  //cAngleWall.FromEulerAngles(CRadians::PI_OVER_FOUR, CRadians::ZERO, CRadians::ZERO);
  //pcWall = new CBoxEntity("wall_east_north_east",
  //    CVector3(m_fPosMiddle*1.5, m_fPosMiddle*0.5, 0.0), // Position
  //    cAngleWall,
  //    false,
  //    CVector3(WIDTH_WALLS, m_fLengthSide/2, HEIGHT_WALLS));   // Size
  //AddEntity(*pcWall);
//
  //cAngleWall.FromEulerAngles(CRadians::PI_OVER_TWO, CRadians::ZERO, CRadians::ZERO);
  //pcWall = new CBoxEntity("wall_north",
  //    CVector3(0, m_fPosMiddle, 0.0), // Position
  //    cAngleWall,
  //    false,
  //    CVector3(WIDTH_WALLS, m_fPosMiddle*2, HEIGHT_WALLS));   // Size
  //AddEntity(*pcWall);
//
  //cAngleWall.FromEulerAngles(-CRadians::PI_OVER_FOUR, CRadians::ZERO, CRadians::ZERO);
  //pcWall = new CBoxEntity("wall_west_north_west",
  //    CVector3(-m_fPosMiddle*1.5, m_fPosMiddle*0.5, 0.0), // Position
  //    cAngleWall,
  //    false,
  //    CVector3(WIDTH_WALLS, m_fLengthSide/2, HEIGHT_WALLS));   // Size
  //AddEntity(*pcWall);

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
       bPlaced = MoveEntity(pcFootBot->GetEmbodiedEntity(),
                            cFootBotPosition,
                            CQuaternion().FromEulerAngles(m_pcRNG->Uniform(CRange<CRadians>(CRadians::ZERO,CRadians::TWO_PI)),
                            CRadians::ZERO,CRadians::ZERO),false);
    } while(!bPlaced && unTrials < 100);
    if(!bPlaced) {
       THROW_ARGOSEXCEPTION("Can't place robot");
    }
  }
}

/****************************************/
/****************************************/

CVector3 CForaging::GetRandomPosition() {
  Real a = m_pcRNG->Uniform(CRange<Real>(-1.0f, 1.0f));
  Real b = m_pcRNG->Uniform(CRange<Real>(-1.0f, 1.0f));
  return CVector3(a*SPAWN_SIDE_LENGTH, b*SPAWN_SIDE_LENGTH, 0.0f);
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
