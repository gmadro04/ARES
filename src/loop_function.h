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
   /**
    * Saves the final positions of robots in the "posiciones.txt" file and
    * Data .
    */
   void SaveRobotPositions();
   void SaveExperimentData();
   //std::vector<CVector2> m_vCirclePositions;


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
     * Número de círculos
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
    // /**
    // * Id mision y comportamiento
    // */
    //size_t m_unIDmision;
    // /**
    // * Tamaño de arena
    // */
    //size_t m_unCirclebool;
    /**
     * Posiciones de los círculos negros
     */
    std::vector<CVector2> m_vCirclePositions;
    //CVector2 m_vCirclePositions;


   /**
     * Method used to create and distribute the Arena.
     */
    void PositionArena();
    void ComputeCirclePositions(UInt32 NumCircles);


    CRadians ComputeOrientation(CVector2 vec_a, CVector2 vec_b);
    CVector2 ComputeMiddle(CVector2 vec_a, CVector2 vec_b);

    bool IsWithinTriangle(CVector2& c_point, CVector2& c_point_a, CVector2& c_point_b, CVector2& c_point_c);
    Real AreaTriangle(CVector2& c_point_a, CVector2& c_point_b, CVector2& c_point_c);
    bool IsWithinWalls(CVector2& c_position);

    CVector2 m_cCoordSource;
    CVector2 m_cCoordNest;
};
