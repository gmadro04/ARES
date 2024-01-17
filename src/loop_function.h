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

#include <fstream>
#include <algorithm>
#include <cstring>
#include <cerrno>

using namespace argos;

static const UInt8  NUM_ROBOTS             = 30;

class CForaging : public CLoopFunctions {

public:

   /**
    * Class constructor
    */
   CForaging();

   /**
    * Class destructor
    */
   virtual ~CForaging();

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

   bool IsOnNest(CVector2& c_position_robot);

   bool IsOnSource(CVector2& c_position_robot);

   bool IsOnForbidden(CVector2& c_position_robot);
   /**
    * Funciones de posicionamiento
    * 
   */
   double Asignar_tamano_segun_arena(const std::string& arena_tipo);
   bool Dentro_del_triangulo(const std::pair<double, double>& punto, double tam);
   bool Dentro_del_circulo(const std::pair<double,double>& punto, double tam);
   /**
    * Saves the final positions of robots in the "posiciones.txt" file and
    * Data .
    */
   void SaveRobotPositions();
   void SaveExperimentData();
   //std::vector<CVector2> m_vCirclePositions;
   /*
   METRICAS MISION
   */
   // FUNCION QUE LLAMA A LA METRICA A EVALUAR
   void ScoreControl();
   void UpdateRobotPositions();
   // --- Función para obtener la puntuación de agregación
   Real GetAggregationScore();
   // Función para verificar si el robot está dentro del círculo de agregación
   bool IsRobotInAggCircle(Real x, Real y);
   // Función para actualizar el tiempo de agregación
   void UpdateAggregationTime();
   // --- Función para obtener la puntuación de exploración
   Real GetExplorationScore(); 
   // -- Función para obtener la puntuación de marcha en formación
   Real GetPatternFormationScore();

private:

   /**
    * The path of the output file.
    */
   std::string m_strOutFile;

   /**
    * The stream associated to the output file.
    */
   std::ofstream m_cOutFile;

   /**
    * Keeps track of the food carried by the robots.
    */
   SInt8 m_sFoodData[NUM_ROBOTS];
   /**
    * Number of items collected in foraging
    */
   UInt32 m_unNbrItemsCollected;

   /**
    * Time step counter
    */
   UInt32 m_unTimeStep;

   /**
    * Random number generator
    */
   CRandom::CRNG* m_pcRNG;

    /**
     * Número de círculos en la arena
     */
    size_t m_unNumCircles;
    /**
     * Número de ejecución
     */
    size_t m_unExperiment;
    /**
    // * Tipo de arena
    // */
    std::string m_unArenatype;
    ///**
    // * Tamaño de arena
    // */
    std::string m_unArenatam;
    // * Semilla aleatorea
    // */
    std::string m_unSeed;
    // /**
    // * Id mision y comportamiento
    // */
    size_t m_unIDmision;
    // /**
    // * Numero de robots
    size_t m_unRobots;
    // Obstaculos en la arena*/
    std::string m_unObsbool;
    /**
     * Posiciones de los círculos negros y elementos
     */
    std::vector<CVector2> m_vCirclePositions;
    std::vector<CVector2> m_vElementsPositions;
    //CVector2 m_vCirclePositions;


   /**
     * Method used to create and distribute the Arena.
     */
    void PositionArena();
    void ComputeCirclePositions(UInt32 NumCircles);
    void InitRobotStates();
    CVector2 GetRandomPositionInHexagon(double tam);

    CRadians ComputeOrientation(CVector2 vec_a, CVector2 vec_b);
    CVector2 ComputeMiddle(CVector2 vec_a, CVector2 vec_b);

    bool IsWithinTriangle(CVector2& c_point, CVector2& c_point_a, CVector2& c_point_b, CVector2& c_point_c);
    Real AreaTriangle(CVector2& c_point_a, CVector2& c_point_b, CVector2& c_point_c);

    CVector2 m_cCoordSource;
    CVector2 m_cCoordNest;
    // Variables de las misiones
    Real m_fObjectiveFunction; // funcion objetio para cada mision 
    // ---------- Variables de Exploración ----------
    std::vector<std::vector<int>> m_grid;
    Real m_arenaSize; // Varaiable Exploración
    UInt32 m_gridSize; // cuadricula Exploración
    std::vector<bool> grid;
    CVector2 sizeArena;
	 Real maxScore;
    // ----- Marcha en formación
    UInt32 m_unNumberPoints;

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
