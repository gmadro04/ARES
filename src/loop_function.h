#include <argos3/core/simulator/simulator.h>
#include <argos3/core/simulator/space/space.h>
#include <argos3/plugins/simulator/entities/cylinder_entity.h>
#include <argos3/plugins/simulator/entities/light_entity.h>
#include <argos3/plugins/simulator/entities/led_entity.h>
#include <argos3/plugins/simulator/media/led_medium.h>
#include <argos3/core/simulator/loop_functions.h>
#include <argos3/plugins/simulator/entities/box_entity.h>
#include <argos3/plugins/robots/foot-bot/simulator/footbot_entity.h>
#include <argos3/core/utility/math/rng.h>

#include <argos3/core/utility/math/rng.h>
#include <argos3/core/simulator/entity/embodied_entity.h>
#include <argos3/core/simulator/entity/controllable_entity.h>
#include <argos3/core/utility/math/vector2.h>
#include <argos3/core/utility/math/vector3.h>
#include <argos3/plugins/robots/generic/control_interface/ci_range_and_bearing_sensor.h>
#include <argos3/core/utility/logging/argos_log.h>
/* Definition of the CCI_Controller class. */
#include <argos3/core/control_interface/ci_controller.h>
/* Definition of the differential steering actuator */
#include <argos3/plugins/robots/generic/control_interface/ci_differential_steering_actuator.h>
/* Definition of proximity sensor */
#include <argos3/plugins/robots/generic/control_interface/ci_proximity_sensor.h>

#include <fstream>
#include <algorithm>
#include <cstring>
#include <cerrno>

using namespace argos;

class CSwarmGenerator : public CLoopFunctions {

public:

   /**
    * Class constructor
    */
   CSwarmGenerator();

   /**
    * Class destructor
    */
   virtual ~CSwarmGenerator();

   /**
    * Initializes the experiment.
    * It is executed once at the beginning of the experiment, i.e., when ARGoS is launched.
    * @param t_tree The parsed XML tree corresponding to the <loop_functions> section.
    */
   virtual void Init(TConfigurationNode& t_tree);
   virtual void Init();

   CVector3 GetRandomPosition();
   CVector2 GetRandomPoint();
   void MoveRobots();
   void InitializeArena();

   /**
    * Resets the experiment to the state it was right after Init() was called.
    * It is executed every time you press the 'reset' button in the GUI.
    */
   virtual void Reset();

   /**
    * Undoes whatever Init() did.
    * It is executed once when ARGoS has finished the experiment.
    */
   virtual void Destroy();

   /**
    * Performs actions right before a simulation step is executed.
    */
   virtual void PreStep();

   /**
    * Performs actions right after a simulation step is executed.
    */
   virtual void PostStep();

   virtual void PostExperiment();

   /**
    * Returns the color of the floor at the specified point on.
    * @param c_position_on_plane The position at which you want to get the color.
    * @see CColor
    */
   virtual CColor GetFloorColor(const CVector2& c_position_on_plane);
   /**
    * Funciones de posicionamiento
    * 
   */
   double Asignar_tamano_segun_arena(const std::string& arena_tipo);
   bool Dentro_del_triangulo(const std::pair<double, double>& punto, double tam);
   bool Dentro_del_circulo(const std::pair<double,double>& punto, double tam);

   /**
    * Saves the Data .
    */
   void SaveExperimentData();
   /*
   METRICAS MISION
   */
   // FUNCION QUE LLAMA A LA METRICA A EVALUAR

   // *****--- Función para obtener la puntuación de agregación ---*****
   Real GetAggregationScore();
   void UpdateRobotPositions(); // Actaliza las posiciones de los robots durante la simulación
   bool IsRobotInAggCircle(Real x, Real y); // Función para verificar si el robot está dentro del círculo de agregación
   void UpdateAggregationTime();    // Función para actualizar el tiempo de agregación
   // *****--- Función para obtener la puntuación de exploración ---*****
   Real GetExplorationScore(); 
   // *****--- Función para obtener la puntuación de marcha en formación ---*****
   Real GetPatternFormationScore();
   // *****--- Función para obtener la puntuación de toma de decisiones ---*****
   Real GetCollectiveDecisionScore();
   // FUNCION DE FALLOS
   void StopRobots();

private:

   /**
    * Categoria del Software de Control.
    */
   std::string m_unSoftware;

   /**
    * Random number generator
    */
   CRandom::CRNG* m_pcRNG;

   /**
    * Número de círculos en la arena
    */
   size_t m_unNumCircles;
   /**
   // * Número de ejecución
   // */
   size_t m_unExperiment;
   // * Tipo de arena
   // */
   std::string m_unArenatype;
   // * Tamaño de arena
   // */
   std::string m_unArenatam;
   // * Semilla aleatorea
   // */
   std::string m_unSeed;
   // * Fallos en el enjambre
   // */
   std::string m_unFaults;
   // * Id mision y comportamiento
   // */
   size_t m_unIDmision;
   // * Numero de robots
   // */
   size_t m_unRobots;
   // Obstaculos en la arena*/
   //std::string m_unObsbool;

   /**
    * Posiciones de los círculos negros y elementos
    */
   std::vector<CVector2> m_vCirclePositions;
   std::vector<CVector2> m_vElementsPositions;


   /**
   * Method used to create and distribute the Arena.
   */
   void PositionArena();
   void ComputeCirclePositions(UInt32 NumCircles);
   void InitRobotStates();
   // variable para controlar fallos 
   bool fallos;

   CRadians ComputeOrientation(CVector2 vec_a, CVector2 vec_b);
   CVector2 ComputeMiddle(CVector2 vec_a, CVector2 vec_b);
   CVector2 m_cCoordSource;
   CVector2 m_cCoordNest;
   // Variables de las misiones
   Real m_fObjectiveFunction; // funcion objetio para cada mision
   // variable para acceder a los motores del robot
   CCI_DifferentialSteeringActuator* m_pcWheels;
   // ---------- Variables de Exploración ----------
   std::vector<std::vector<int>> m_grid;
   Real m_arenaSize; // Varaiable Exploración
   UInt32 m_gridSize; // cuadricula Exploración
   std::vector<bool> grid;
   CVector2 sizeArena;
	Real maxScore;
   // ----- Marcha en formación
   UInt32 m_unNumberPoints;
   // ----- TOma de decisiones
   bool consenso;
   UInt32 tiempo_conseso;
   void RegisterPositions();



   struct RobotStateStruct {
      CVector2 cLastPosition;
      CVector2 cPosition;
      UInt32 unItem;
      Real FTimeInAgg;
   };

   typedef std::map<argos::CFootBotEntity*, RobotStateStruct> TRobotStateMap;
   TRobotStateMap m_tRobotStates;
};
