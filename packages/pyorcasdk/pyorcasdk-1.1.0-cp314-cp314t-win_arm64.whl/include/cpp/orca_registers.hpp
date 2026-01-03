#ifndef ORCA_REGISTERS_HPP
#define ORCA_REGISTERS_HPP

#include <cstdint>

namespace ORCAReg {
    /* Beginning of Register Addresses */
    constexpr int CTRL_REG_0                = 0;
    constexpr int CTRL_REG_1                = 1;
    constexpr int CTRL_REG_2                = 2;
    constexpr int CTRL_REG_3                = 3;
    constexpr int CTRL_REG_4                = 4;
    constexpr int KIN_SW_TRIGGER            = 9;
    constexpr int FORCE_CMD                 = 28;
    constexpr int FORCE_CMD_H               = 29;
    constexpr int POS_CMD                   = 30;
    constexpr int POS_CMD_H                 = 31;
    constexpr int CC_PGAIN                  = 129;
    constexpr int CC_IGAIN                  = 130;
    constexpr int CC_FGAIN                  = 131;
    constexpr int PC_PGAIN                  = 133;
    constexpr int PC_IGAIN                  = 134;
    constexpr int PC_DVGAIN                 = 135;
    constexpr int PC_DEGAIN                 = 136;
    constexpr int PC_FSATU                  = 137;
    constexpr int PC_FSATU_H                = 138;
    constexpr int USER_MAX_TEMP             = 139;
    constexpr int USER_MAX_FORCE            = 140;
    constexpr int USER_MAX_FORCE_H          = 141;
    constexpr int USER_MAX_POWER            = 142;
    constexpr int SAFETY_DGAIN              = 143;
    constexpr int USER_MAX_COIL_TEMP        = 147;
    constexpr int TEMP_ERR_HYSTERESIS       = 148;
    constexpr int PC_SOFTSTART_PERIOD       = 150;
    constexpr int FORCE_UNITS               = 151;
    constexpr int POS_SIGN                  = 152;
    constexpr int POS_MAX_VEL               = 153;
    constexpr int POS_MAX_ACCEL             = 154;
    constexpr int POS_MAX_DECEL             = 155;
    constexpr int LOG_PERIOD                = 162;
    constexpr int USER_COMMS_TIMEOUT        = 163;
    constexpr int USR_MB_BAUD_LO            = 164;
    constexpr int USR_MB_BAUD_HI            = 165;
    constexpr int FORCE_FILT                = 166;
    constexpr int POS_FILT                  = 167;
    constexpr int USR_MB_DELAY              = 168;
    constexpr int USR_MB_ADDR               = 169;
    constexpr int ZERO_MODE                 = 171;
    constexpr int AUTO_ZERO_FORCE_N         = 172;
    constexpr int AUTO_ZERO_EXIT_MODE       = 173;
    constexpr int MB_RS485_MODE             = 174;
    constexpr int MB_FORCE_FILTER           = 175;
    constexpr int MB_POS_FILTER             = 176;
    constexpr int AUTO_ZERO_SPEED_MMPS      = 177;
    constexpr int PWM_TIMEOUT_MS            = 178;
    constexpr int PWM_TIME_CONST_MS         = 179;
    constexpr int PWM_MIN_POS               = 180;
    constexpr int PWM_MIN_POS_H             = 181;
    constexpr int PWM_MAX_POS               = 182;
    constexpr int PWM_MAX_POS_H             = 183;
    constexpr int PWM_SERVO_TYPE            = 184;
    constexpr int MB_FREQ                   = 273;
    constexpr int MODE_OF_OPERATION         = 317;
    constexpr int KINEMATIC_STATUS          = 319;
    constexpr int KIN_COMPLETE_COUNT        = 320;
    constexpr int MOTOR_STATUS              = 321;
    constexpr int POS_CURSOR                = 322;
    constexpr int POS_CURSOR_H              = 323;
    constexpr int BOARD_TEMP                = 336;
    constexpr int VDD_FINAL                 = 338;
    constexpr int SHAFT_POS_UM              = 342;
    constexpr int SHAFT_POSITION_H          = 343;
    constexpr int SHAFT_SPEED_MMPS          = 344;
    constexpr int SHAFT_SHEED_H             = 345;
    constexpr int SHAFT_ACCEL_MMPSS         = 346;
    constexpr int SHAFT_ACCEL_H             = 347;
    constexpr int FORCE                     = 348;
    constexpr int FORCE_H                   = 349;
    constexpr int POWER                     = 350;
    constexpr int HBA_CURRENT               = 351;
    constexpr int HBB_CURRENT               = 352;
    constexpr int HBC_CURRENT               = 353;
    constexpr int HBD_CURRENT               = 354;
    constexpr int AVG_POWER                 = 355;
    constexpr int COIL_TEMP                 = 356;
    constexpr int SERIAL_NUMBER_LOW         = 406;
    constexpr int SERIAL_NUMBER_HIGH        = 407;
    constexpr int MAJOR_VERSION             = 408;
    constexpr int RELEASE_STATE             = 409;
    constexpr int REVISION_NUMBER           = 410;
    constexpr int COMMIT_ID_LO              = 411;
    constexpr int COMMIT_ID_HI              = 412;
    constexpr int STATOR_CONFIG             = 418;
    constexpr int WARNING                   = 431;
    constexpr int ERROR_0                   = 432;
    constexpr int ERROR_1                   = 433;
    constexpr int MB_CNT0                   = 464;
    constexpr int MB_CNT1                   = 465;
    constexpr int MB_CNT2                   = 466;
    constexpr int MB_CNT3                   = 467;
    constexpr int MB_CNT4                   = 468;
    constexpr int MB_CNT5                   = 469;
    constexpr int MB_CNT6                   = 470;
    constexpr int MB_CNT7                   = 471;
    constexpr int MB_CNT8                   = 472;
    constexpr int MB_CNT9                   = 473;
    constexpr int MB_CNT10                  = 474;
    constexpr int MB_CNT11                  = 475;
    constexpr int MB_CNT12                  = 476;
    constexpr int MB_CNT13                  = 477;
    constexpr int MB_CNT14                  = 478;
    constexpr int MB_BAUD                   = 482;
    constexpr int MB_BAUD_H                 = 483;
    constexpr int MB_IF_DELAY               = 484;
    constexpr int MB_ADDRESS                = 485;
    constexpr int HAPTIC_STATUS             = 641;
    constexpr int CONSTANT_FORCE_MN         = 642;
    constexpr int CONSTANT_FORCE_MN_H       = 643;
    constexpr int S0_GAIN_N_MM              = 644;
    constexpr int S0_CENTER_UM              = 645;
    constexpr int S0_CENTER_UM_H            = 646;
    constexpr int S0_COUPLING               = 647;
    constexpr int S0_DEAD_ZONE_MM           = 648;
    constexpr int S0_FORCE_SAT_N            = 649;
    constexpr int S1_GAIN_N_MM              = 650;
    constexpr int S1_CENTER_UM              = 651;
    constexpr int S1_CENTER_UM_H            = 652;
    constexpr int S1_COUPLING               = 653;
    constexpr int S1_DEAD_ZONE_MM           = 654;
    constexpr int S1_FORCE_SAT_N            = 655;
    constexpr int S2_GAIN_N_MM              = 656;
    constexpr int S2_CENTER_UM              = 657;
    constexpr int S2_CENTER_UM_H            = 658;
    constexpr int S2_COUPLING               = 659;
    constexpr int S2_DEAD_ZONE_MM           = 660;
    constexpr int S2_FORCE_SAT_N            = 661;
    constexpr int D0_GAIN_NS_MM             = 662;
    constexpr int I0_GAIN_NS2_MM            = 663;
    constexpr int O0_GAIN_N                 = 664;
    constexpr int O0_TYPE                   = 665;
    constexpr int O0_FREQ_DHZ               = 666;
    constexpr int O0_DUTY                   = 667;
    constexpr int O1_GAIN_N                 = 668;
    constexpr int O1_TYPE                   = 669;
    constexpr int O1_FREQ_DHZ               = 670;
    constexpr int O1_DUTY                   = 671;
    constexpr int CONST_FORCE_FILTER        = 672;
    constexpr int HAPTIC_SOFTSTART          = 673;
    constexpr int ILOOP_DIN                 = 756;
    constexpr int ILOOP_OUT_CH1             = 757;
    constexpr int ILOOP_OUT_CH2             = 758;
    constexpr int ILOOP_IN                  = 759;
    constexpr int ILOOP_CONFIG              = 761;
    constexpr int ILOOP_FORCE_MIN           = 762;
    constexpr int ILOOP_FORCE_MIN_HI        = 763;
    constexpr int ILOOP_FORCE_MAX           = 764;
    constexpr int ILOOP_FORCE_MAX_HI        = 765;
    constexpr int ILOOP_POS_MIN             = 766;
    constexpr int ILOOP_POS_MIN_HI          = 767;
    constexpr int ILOOP_POS_MAX             = 768;
    constexpr int ILOOP_POS_MAX_HI          = 769;
    constexpr int ILOOP_KIN_TYPE            = 770;
    constexpr int ILOOP_D0_HIGH_ID          = 771;
    constexpr int ILOOP_D0_LOW_ID           = 772;
    constexpr int ILOOP_D1_HIGH_ID          = 773;
    constexpr int ILOOP_D1_LOW_ID           = 774;
    constexpr int ILOOP_D2_HIGH_ID          = 775;
    constexpr int ILOOP_D2_LOW_ID           = 776;
    constexpr int KIN0_POSITION_TARGET      = 780;
    constexpr int KIN0_POSITION_TARGET_H    = 781;
    constexpr int KIN0_MOTION_TIME          = 782;
    constexpr int KIN0_MOTION_TIME_H        = 783;
    constexpr int KIN0_DELAY_TIME           = 784;
    constexpr int KIN0_MOTION_CONFIG        = 785;
    constexpr int KIN1_POSITION_TARGET      = 786;
    constexpr int KIN1_POSITION_TARGET_H    = 787;
    constexpr int KIN1_MOTION_TIME          = 788;
    constexpr int KIN1_MOTION_TIME_H        = 789;
    constexpr int KIN1_DELAY_TIME           = 790;
    constexpr int KIN1_MOTION_CONFIG        = 791;
    constexpr int KIN2_POSITION_TARGET      = 792;
    constexpr int KIN2_POSITION_TARGET_H    = 793;
    constexpr int KIN2_MOTION_TIME          = 794;
    constexpr int KIN2_MOTION_TIME_H        = 795;
    constexpr int KIN2_DELAY_TIME           = 796;
    constexpr int KIN2_MOTION_CONFIG        = 797;
    constexpr int KIN3_POSITION_TARGET      = 798;
    constexpr int KIN3_POSITION_TARGET_H    = 799;
    constexpr int KIN3_MOTION_TIME          = 800;
    constexpr int KIN3_MOTION_TIME_H        = 801;
    constexpr int KIN3_DELAY_TIME           = 802;
    constexpr int KIN3_MOTION_CONFIG        = 803;
    constexpr int KIN4_POSITION_TARGET      = 804;
    constexpr int KIN4_POSITION_TARGET_H    = 805;
    constexpr int KIN4_MOTION_TIME          = 806;
    constexpr int KIN4_MOTION_TIME_H        = 807;
    constexpr int KIN4_DELAY_TIME           = 808;
    constexpr int KIN4_MOTION_CONFIG        = 809;
    constexpr int KIN5_POSITION_TARGET      = 810;
    constexpr int KIN5_POSITION_TARGET_H    = 811;
    constexpr int KIN5_MOTION_TIME          = 812;
    constexpr int KIN5_MOTION_TIME_H        = 813;
    constexpr int KIN5_DELAY_TIME           = 814;
    constexpr int KIN5_MOTION_CONFIG        = 815;
    constexpr int KIN6_POSITION_TARGET      = 816;
    constexpr int KIN6_POSITION_TARGET_H    = 817;
    constexpr int KIN6_MOTION_TIME          = 818;
    constexpr int KIN6_MOTION_TIME_H        = 819;
    constexpr int KIN6_DELAY_TIME           = 820;
    constexpr int KIN6_MOTION_CONFIG        = 821;
    constexpr int KIN7_POSITION_TARGET      = 822;
    constexpr int KIN7_POSITION_TARGET_H    = 823;
    constexpr int KIN7_MOTION_TIME          = 824;
    constexpr int KIN7_MOTION_TIME_H        = 825;
    constexpr int KIN7_DELAY_TIME           = 826;
    constexpr int KIN7_MOTION_CONFIG        = 827;
    constexpr int KIN8_POSITION_TARGET      = 828;
    constexpr int KIN8_POSITION_TARGET_H    = 829;
    constexpr int KIN8_MOTION_TIME          = 830;
    constexpr int KIN8_MOTION_TIME_H        = 831;
    constexpr int KIN8_DELAY_TIME           = 832;
    constexpr int KIN8_MOTION_CONFIG        = 833;
    constexpr int KIN9_POSITION_TARGET      = 834;
    constexpr int KIN9_POSITION_TARGET_H    = 835;
    constexpr int KIN9_MOTION_TIME          = 836;
    constexpr int KIN9_MOTION_TIME_H        = 837;
    constexpr int KIN9_DELAY_TIME           = 838;
    constexpr int KIN9_MOTION_CONFIG        = 839;
    constexpr int KIN10_POSITION_TARGET     = 840;
    constexpr int KIN10_POSITION_TARGET_H   = 841;
    constexpr int KIN10_MOTION_TIME         = 842;
    constexpr int KIN10_MOTION_TIME_H       = 843;
    constexpr int KIN10_DELAY_TIME          = 844;
    constexpr int KIN10_MOTION_CONFIG       = 845;
    constexpr int KIN11_POSITION_TARGET     = 846;
    constexpr int KIN11_POSITION_TARGET_H   = 847;
    constexpr int KIN11_MOTION_TIME         = 848;
    constexpr int KIN11_MOTION_TIME_H       = 849;
    constexpr int KIN11_DELAY_TIME          = 850;
    constexpr int KIN11_MOTION_CONFIG       = 851;
    constexpr int KIN12_POSITION_TARGET     = 852;
    constexpr int KIN12_POSITION_TARGET_H   = 853;
    constexpr int KIN12_MOTION_TIME         = 854;
    constexpr int KIN12_MOTION_TIME_H       = 855;
    constexpr int KIN12_DELAY_TIME          = 856;
    constexpr int KIN12_MOTION_CONFIG       = 857;
    constexpr int KIN13_POSITION_TARGET     = 858;
    constexpr int KIN13_POSITION_TARGET_H   = 859;
    constexpr int KIN13_MOTION_TIME         = 860;
    constexpr int KIN13_MOTION_TIME_H       = 861;
    constexpr int KIN13_DELAY_TIME          = 862;
    constexpr int KIN13_MOTION_CONFIG       = 863;
    constexpr int KIN14_POSITION_TARGET     = 864;
    constexpr int KIN14_POSITION_TARGET_H   = 865;
    constexpr int KIN14_MOTION_TIME         = 866;
    constexpr int KIN14_MOTION_TIME_H       = 867;
    constexpr int KIN14_DELAY_TIME          = 868;
    constexpr int KIN14_MOTION_CONFIG       = 869;
    constexpr int KIN15_POSITION_TARGET     = 870;
    constexpr int KIN15_POSITION_TARGET_H   = 871;
    constexpr int KIN15_MOTION_TIME         = 872;
    constexpr int KIN15_MOTION_TIME_H       = 873;
    constexpr int KIN15_DELAY_TIME          = 874;
    constexpr int KIN15_MOTION_CONFIG       = 875;
    constexpr int KIN16_POSITION_TARGET     = 876;
    constexpr int KIN16_POSITION_TARGET_H   = 877;
    constexpr int KIN16_MOTION_TIME         = 878;
    constexpr int KIN16_MOTION_TIME_H       = 879;
    constexpr int KIN16_DELAY_TIME          = 880;
    constexpr int KIN16_MOTION_CONFIG       = 881;
    constexpr int KIN17_POSITION_TARGET     = 882;
    constexpr int KIN17_POSITION_TARGET_H   = 883;
    constexpr int KIN17_MOTION_TIME         = 884;
    constexpr int KIN17_MOTION_TIME_H       = 885;
    constexpr int KIN17_DELAY_TIME          = 886;
    constexpr int KIN17_MOTION_CONFIG       = 887;
    constexpr int KIN18_POSITION_TARGET     = 888;
    constexpr int KIN18_POSITION_TARGET_H   = 889;
    constexpr int KIN18_MOTION_TIME         = 890;
    constexpr int KIN18_MOTION_TIME_H       = 891;
    constexpr int KIN18_DELAY_TIME          = 892;
    constexpr int KIN18_MOTION_CONFIG       = 893;
    constexpr int KIN19_POSITION_TARGET     = 894;
    constexpr int KIN19_POSITION_TARGET_H   = 895;
    constexpr int KIN19_MOTION_TIME         = 896;
    constexpr int KIN19_MOTION_TIME_H       = 897;
    constexpr int KIN19_DELAY_TIME          = 898;
    constexpr int KIN19_MOTION_CONFIG       = 899;
    constexpr int KIN20_POSITION_TARGET     = 900;
    constexpr int KIN20_POSITION_TARGET_H   = 901;
    constexpr int KIN20_MOTION_TIME         = 902;
    constexpr int KIN20_MOTION_TIME_H       = 903;
    constexpr int KIN20_DELAY_TIME          = 904;
    constexpr int KIN20_MOTION_CONFIG       = 905;
    constexpr int KIN21_POSITION_TARGET     = 906;
    constexpr int KIN21_POSITION_TARGET_H   = 907;
    constexpr int KIN21_MOTION_TIME         = 908;
    constexpr int KIN21_MOTION_TIME_H       = 909;
    constexpr int KIN21_DELAY_TIME          = 910;
    constexpr int KIN21_MOTION_CONFIG       = 911;
    constexpr int KIN22_POSITION_TARGET     = 912;
    constexpr int KIN22_POSITION_TARGET_H   = 913;
    constexpr int KIN22_MOTION_TIME         = 914;
    constexpr int KIN22_MOTION_TIME_H       = 915;
    constexpr int KIN22_DELAY_TIME          = 916;
    constexpr int KIN22_MOTION_CONFIG       = 917;
    constexpr int KIN23_POSITION_TARGET     = 918;
    constexpr int KIN23_POSITION_TARGET_H   = 919;
    constexpr int KIN23_MOTION_TIME         = 920;
    constexpr int KIN23_MOTION_TIME_H       = 921;
    constexpr int KIN23_DELAY_TIME          = 922;
    constexpr int KIN23_MOTION_CONFIG       = 923;
    constexpr int KIN24_POSITION_TARGET     = 924;
    constexpr int KIN24_POSITION_TARGET_H   = 925;
    constexpr int KIN24_MOTION_TIME         = 926;
    constexpr int KIN24_MOTION_TIME_H       = 927;
    constexpr int KIN24_DELAY_TIME          = 928;
    constexpr int KIN24_MOTION_CONFIG       = 929;
    constexpr int KIN25_POSITION_TARGET     = 930;
    constexpr int KIN25_POSITION_TARGET_H   = 931;
    constexpr int KIN25_MOTION_TIME         = 932;
    constexpr int KIN25_MOTION_TIME_H       = 933;
    constexpr int KIN25_DELAY_TIME          = 934;
    constexpr int KIN25_MOTION_CONFIG       = 935;
    constexpr int KIN26_POSITION_TARGET     = 936;
    constexpr int KIN26_POSITION_TARGET_H   = 937;
    constexpr int KIN26_MOTION_TIME         = 938;
    constexpr int KIN26_MOTION_TIME_H       = 939;
    constexpr int KIN26_DELAY_TIME          = 940;
    constexpr int KIN26_MOTION_CONFIG       = 941;
    constexpr int KIN27_POSITION_TARGET     = 942;
    constexpr int KIN27_POSITION_TARGET_H   = 943;
    constexpr int KIN27_MOTION_TIME         = 944;
    constexpr int KIN27_MOTION_TIME_H       = 945;
    constexpr int KIN27_DELAY_TIME          = 946;
    constexpr int KIN27_MOTION_CONFIG       = 947;
    constexpr int KIN28_POSITION_TARGET     = 948;
    constexpr int KIN28_POSITION_TARGET_H   = 949;
    constexpr int KIN28_MOTION_TIME         = 950;
    constexpr int KIN28_MOTION_TIME_H       = 951;
    constexpr int KIN28_DELAY_TIME          = 952;
    constexpr int KIN28_MOTION_CONFIG       = 953;
    constexpr int KIN29_POSITION_TARGET     = 954;
    constexpr int KIN29_POSITION_TARGET_H   = 955;
    constexpr int KIN29_MOTION_TIME         = 956;
    constexpr int KIN29_MOTION_TIME_H       = 957;
    constexpr int KIN29_DELAY_TIME          = 958;
    constexpr int KIN29_MOTION_CONFIG       = 959;
    constexpr int KIN30_POSITION_TARGET     = 960;
    constexpr int KIN30_POSITION_TARGET_H   = 961;
    constexpr int KIN30_MOTION_TIME         = 962;
    constexpr int KIN30_MOTION_TIME_H       = 963;
    constexpr int KIN30_DELAY_TIME          = 964;
    constexpr int KIN30_MOTION_CONFIG       = 965;
    constexpr int KIN31_POSITION_TARGET     = 966;
    constexpr int KIN31_POSITION_TARGET_H   = 967;
    constexpr int KIN31_MOTION_TIME         = 968;
    constexpr int KIN31_MOTION_TIME_H       = 969;
    constexpr int KIN31_DELAY_TIME          = 970;
    constexpr int KIN31_MOTION_CONFIG       = 971;
    constexpr int KIN_HOME_ID               = 972;

    /* Beginning of Register Value Definitions */

    namespace CTRL_REG_0_Values {
        constexpr uint16_t RESET_ORCA_Mask  = 0x1;
        constexpr uint16_t RESET_ORCA_Shift = 0;
        constexpr uint16_t CLEAR_ERR_Mask   = 0x2;
        constexpr uint16_t CLEAR_ERR_Shift  = 1;
        constexpr uint16_t ZERO_POS_Mask    = 0x4;
        constexpr uint16_t ZERO_POS_Shift   = 2;
        constexpr uint16_t INVERT_POS_Mask  = 0x8;
        constexpr uint16_t INVERT_POS_Shift = 3;
    }

    namespace CTRL_REG_1_Values {
        constexpr uint16_t HALL_GAIN_SET_Mask      = 0x8;
        constexpr uint16_t HALL_GAIN_SET_Shift     = 3;
        constexpr uint16_t CURRENT_GAIN_SET_Mask   = 0x10;
        constexpr uint16_t CURRENT_GAIN_SET_Shift  = 4;
        constexpr uint16_t HALL_ZERO_FLAG_Mask     = 0x20;
        constexpr uint16_t HALL_ZERO_FLAG_Shift    = 5;
        constexpr uint16_t CURRENT_ZERO_FLAG_Mask  = 0x40;
        constexpr uint16_t CURRENT_ZERO_FLAG_Shift = 6;
        constexpr uint16_t PC_GAIN_APPLY_Mask      = 0x400;
        constexpr uint16_t PC_GAIN_APPLY_Shift     = 10;
        constexpr uint16_t CC_GAIN_APPLY_Mask      = 0x800;
        constexpr uint16_t CC_GAIN_APPLY_Shift     = 11;
    }

    namespace CTRL_REG_2_Values {
        constexpr uint16_t STATOR_CAL_SAVE_Mask   = 0x4;
        constexpr uint16_t STATOR_CAL_SAVE_Shift  = 2;
        constexpr uint16_t SHAFT_CAL_SAVE_Mask    = 0x8;
        constexpr uint16_t SHAFT_CAL_SAVE_Shift   = 3;
        constexpr uint16_t FORCE_CAL_SAVE_Mask    = 0x10;
        constexpr uint16_t FORCE_CAL_SAVE_Shift   = 4;
        constexpr uint16_t TUNING_SAVE_Mask       = 0x20;
        constexpr uint16_t TUNING_SAVE_Shift      = 5;
        constexpr uint16_t USER_OPTION_SAVE_Mask  = 0x40;
        constexpr uint16_t USER_OPTION_SAVE_Shift = 6;
        constexpr uint16_t KINEMATIC_SAVE_Mask    = 0x80;
        constexpr uint16_t KINEMATIC_SAVE_Shift   = 7;
        constexpr uint16_t IOSH_SAVE_Mask         = 0x100;
        constexpr uint16_t IOSH_SAVE_Shift        = 8;
        constexpr uint16_t HAPTIC_SAVE_Mask       = 0x200;
        constexpr uint16_t HAPTIC_SAVE_Shift      = 9;
        constexpr uint16_t TRIM_SAVE_Mask         = 0x400;
        constexpr uint16_t TRIM_SAVE_Shift        = 10;
    }

    namespace CTRL_REG_3_Values {
        enum : uint16_t {
            SLEEP_MODE          = 1,
            FORCE_MODE          = 2,
            POSITION_MODE       = 3,
            HAPTIC_MODE         = 4,
            KINEMATIC_MODE      = 5,
            VOLTAGE_MODE        = 6,
            CURRENT_MODE        = 7,
            IOSH_FORCE_MODE     = 8,
            IOSH_POSITION_MODE  = 9,
            IOSH_KINEMATIC_MODE = 10,
            PULSE_WIDTH_MODE    = 11,
            STATOR_CAL_MODE     = 50,
            FORCE_CAL_MODE      = 51,
            SHAFT_CAL_MODE      = 52,
            ADC_CAL_MODE        = 53,
            STEP_TEST_MODE      = 54,
            AUTO_ZERO_MODE      = 55,
        };
    }

    namespace CTRL_REG_4_Values {
        constexpr uint16_t TUNING_DEFAULTS_Mask         = 0x2;
        constexpr uint16_t TUNING_DEFAULTS_Shift        = 1;
        constexpr uint16_t MOTOR_OPTIONS_DEFAULTS_Mask  = 0x4;
        constexpr uint16_t MOTOR_OPTIONS_DEFAULTS_Shift = 2;
        constexpr uint16_t MODBUS_DEFAULTS_Mask         = 0x8;
        constexpr uint16_t MODBUS_DEFAULTS_Shift        = 3;
        constexpr uint16_t KINEMATIC_DEFAULTS_Mask      = 0x10;
        constexpr uint16_t KINEMATIC_DEFAULTS_Shift     = 4;
        constexpr uint16_t HAPTIC_DEFAULTS_Mask         = 0x20;
        constexpr uint16_t HAPTIC_DEFAULTS_Shift        = 5;
        constexpr uint16_t IOSH_DEFAULTS_Mask           = 0x40;
        constexpr uint16_t IOSH_DEFAULTS_Shift          = 6;
        constexpr uint16_t PULSE_WIDTH_DEFAULTS_Mask    = 0x80;
        constexpr uint16_t PULSE_WIDTH_DEFAULTS_Shift   = 7;
    }

    namespace FORCE_UNITS_Values {
        constexpr uint16_t FORCEUNITS_Mask  = 0x1;
        constexpr uint16_t FORCEUNITS_Shift = 0;
    }

    namespace POS_SIGN_Values {
        constexpr uint16_t POSSIGN_Mask  = 0x1;
        constexpr uint16_t POSSIGN_Shift = 0;
    }

    namespace ZERO_MODE_Values {
        enum : uint16_t {
            NEGATIVE_ZEROING  = 0,
            MANUAL_ZEROING    = 1,
            AUTO_ZERO_ENABLED = 2,
            AUTO_ZERO_ON_BOOT = 3,
            IOSH_AUTO_ZEROING = 4,
        };
    }

    namespace AUTO_ZERO_EXIT_MODE_Values {
        enum : uint16_t {
            SLEEP_MODE       = 1,
            FORCE_MODE       = 2,
            POSITION_MODE    = 3,
            HAPTIC_MODE      = 4,
            KINEMATIC_MODE   = 5,
            PULSE_WIDTH_MODE = 11,
        };
    }

    namespace MB_RS485_MODE_Values {
        constexpr uint16_t RS485MODE_Mask  = 0x1;
        constexpr uint16_t RS485MODE_Shift = 0;
    }

    namespace PWM_SERVO_TYPE_Values {
        enum : uint16_t {
            PWM_180_DEG = 0,
            PWM_270_DEG = 1,
        };
    }

    namespace MODE_OF_OPERATION_Values {
        enum : uint16_t {
            SLEEP_MODE          = 1,
            FORCE_MODE          = 2,
            POSITION_MODE       = 3,
            HAPTIC_MODE         = 4,
            KINEMATIC_MODE      = 5,
            VOLTAGE_MODE        = 6,
            CURRENT_MODE        = 7,
            IOSH_FORCE_MODE     = 8,
            IOSH_POSITION_MODE  = 9,
            IOSH_KINEMATIC_MODE = 10,
            PULSE_WIDTH_MODE    = 11,
            STATOR_CAL_MODE     = 50,
            FORCE_CAL_MODE      = 51,
            SHAFT_CAL_MODE      = 52,
            ADC_CAL_MODE        = 53,
            STEP_TEST_MODE      = 54,
            AUTO_ZERO_MODE      = 55,
        };
    }

    namespace KINEMATIC_STATUS_Values {
        constexpr uint16_t MOTIONID_Mask  = 0x7FFF;
        constexpr uint16_t MOTIONID_Shift = 0;
        constexpr uint16_t RUNNING_Mask   = 0x8000;
        constexpr uint16_t RUNNING_Shift  = 15;
    }

    namespace MOTOR_STATUS_Values {
        constexpr uint16_t AUTO_ZERO_COMPLETE_Mask  = 0x1;
        constexpr uint16_t AUTO_ZERO_COMPLETE_Shift = 0;
        constexpr uint16_t AUTO_ZERO_RUNNING_Mask   = 0x2;
        constexpr uint16_t AUTO_ZERO_RUNNING_Shift  = 1;
        constexpr uint16_t POS_MODE_MOVING_Mask     = 0x4;
        constexpr uint16_t POS_MODE_MOVING_Shift    = 2;
    }

    namespace STATOR_CONFIG_Values {
        enum : uint16_t {
            ORCA_6_24  = 0,
            ORCA_6_48  = 1,
            ORCA_15_48 = 2,
            ORCA_3_12  = 3,
            ORCA_3_36  = 4,
        };
    }

    namespace WARNING_Values {
        constexpr uint16_t IOSH_AUTO_ZERO_Mask  = 0x1;
        constexpr uint16_t IOSH_AUTO_ZERO_Shift = 0;
    }

    namespace ERROR_0_Values {
        constexpr uint16_t CONFIG_INVALID_Mask          = 0x1;
        constexpr uint16_t CONFIG_INVALID_Shift         = 0;
        constexpr uint16_t FORCE_CONTROL_CLIPPING_Mask  = 0x20;
        constexpr uint16_t FORCE_CONTROL_CLIPPING_Shift = 5;
        constexpr uint16_t MAX_TEMP_EXCEEDED_Mask       = 0x40;
        constexpr uint16_t MAX_TEMP_EXCEEDED_Shift      = 6;
        constexpr uint16_t MAX_FORCE_EXCEEDED_Mask      = 0x80;
        constexpr uint16_t MAX_FORCE_EXCEEDED_Shift     = 7;
        constexpr uint16_t MAX_POWER_EXCEEDED_Mask      = 0x100;
        constexpr uint16_t MAX_POWER_EXCEEDED_Shift     = 8;
        constexpr uint16_t SHAFT_IMAGE_FAILED_Mask      = 0x200;
        constexpr uint16_t SHAFT_IMAGE_FAILED_Shift     = 9;
        constexpr uint16_t VOLTAGE_INVALID_Mask         = 0x400;
        constexpr uint16_t VOLTAGE_INVALID_Shift        = 10;
        constexpr uint16_t COMMS_TIMEOUT_Mask           = 0x800;
        constexpr uint16_t COMMS_TIMEOUT_Shift          = 11;
        constexpr uint16_t AUTO_ZERO_FAILED_Mask        = 0x2000;
        constexpr uint16_t AUTO_ZERO_FAILED_Shift       = 13;
    }

    namespace ERROR_1_Values {
        constexpr uint16_t CONFIG_INVALID_Mask          = 0x1;
        constexpr uint16_t CONFIG_INVALID_Shift         = 0;
        constexpr uint16_t FORCE_CONTROL_CLIPPING_Mask  = 0x20;
        constexpr uint16_t FORCE_CONTROL_CLIPPING_Shift = 5;
        constexpr uint16_t MAX_TEMP_EXCEEDED_Mask       = 0x40;
        constexpr uint16_t MAX_TEMP_EXCEEDED_Shift      = 6;
        constexpr uint16_t MAX_FORCE_EXCEEDED_Mask      = 0x80;
        constexpr uint16_t MAX_FORCE_EXCEEDED_Shift     = 7;
        constexpr uint16_t MAX_POWER_EXCEEDED_Mask      = 0x100;
        constexpr uint16_t MAX_POWER_EXCEEDED_Shift     = 8;
        constexpr uint16_t SHAFT_IMAGE_FAILED_Mask      = 0x200;
        constexpr uint16_t SHAFT_IMAGE_FAILED_Shift     = 9;
        constexpr uint16_t VOLTAGE_INVALID_Mask         = 0x400;
        constexpr uint16_t VOLTAGE_INVALID_Shift        = 10;
        constexpr uint16_t COMMS_TIMEOUT_Mask           = 0x800;
        constexpr uint16_t COMMS_TIMEOUT_Shift          = 11;
        constexpr uint16_t AUTO_ZERO_FAILED_Mask        = 0x2000;
        constexpr uint16_t AUTO_ZERO_FAILED_Shift       = 13;
    }

    namespace HAPTIC_STATUS_Values {
        constexpr uint16_t CONSTANT_Mask      = 0x1;
        constexpr uint16_t CONSTANT_Shift     = 0;
        constexpr uint16_t SPRING_0_Mask      = 0x2;
        constexpr uint16_t SPRING_0_Shift     = 1;
        constexpr uint16_t SPRING_1_Mask      = 0x4;
        constexpr uint16_t SPRING_1_Shift     = 2;
        constexpr uint16_t SPRING_2_Mask      = 0x8;
        constexpr uint16_t SPRING_2_Shift     = 3;
        constexpr uint16_t DAMPER_Mask        = 0x10;
        constexpr uint16_t DAMPER_Shift       = 4;
        constexpr uint16_t INERTIA_Mask       = 0x20;
        constexpr uint16_t INERTIA_Shift      = 5;
        constexpr uint16_t OSCILLATOR_0_Mask  = 0x40;
        constexpr uint16_t OSCILLATOR_0_Shift = 6;
        constexpr uint16_t OSCILLATOR_1_Mask  = 0x80;
        constexpr uint16_t OSCILLATOR_1_Shift = 7;
    }

    namespace Sn_COUPLING_Values {
        enum : uint16_t {
            BOTH     = 0,
            POSITIVE = 1,
            NEGATIVE = 2,
        };
    }

    namespace On_TYPE_Values {
        enum : uint16_t {
            SQUARE   = 0,
            SINE     = 1,
            TRIANGLE = 2,
            SAWTOOTH = 3,
        };
    }

    namespace ILOOP_DIN_Values {
        constexpr uint16_t DIN0_Mask  = 0x1;
        constexpr uint16_t DIN0_Shift = 0;
        constexpr uint16_t DIN1_Mask  = 0x2;
        constexpr uint16_t DIN1_Shift = 1;
        constexpr uint16_t DIN2_Mask  = 0x4;
        constexpr uint16_t DIN2_Shift = 2;
        constexpr uint16_t DIN3_Mask  = 0x8;
        constexpr uint16_t DIN3_Shift = 3;
    }

    namespace ILOOP_CONFIG_Values {
        constexpr uint16_t CH1_Mask      = 0x3;
        constexpr uint16_t CH1_Shift     = 0;
        constexpr uint16_t CH2_Mask      = 0xC;
        constexpr uint16_t CH2_Shift     = 2;
        constexpr uint16_t IN_MODE_Mask  = 0x30;
        constexpr uint16_t IN_MODE_Shift = 4;
        constexpr uint16_t RANGE_Mask    = 0x40;
        constexpr uint16_t RANGE_Shift   = 6;
    }

    namespace ILOOP_KIN_TYPE_Values {
        enum : uint16_t {
            RISING_EDGE = 0,
            BOTH_EDGES  = 1,
        };
    }

    namespace KINn_MOTION_CONFIG_Values {
        constexpr uint16_t CHAIN_Mask    = 0x1;
        constexpr uint16_t CHAIN_Shift   = 0;
        constexpr uint16_t TYPE_Mask     = 0x6;
        constexpr uint16_t TYPE_Shift    = 1;
        constexpr uint16_t CHAINID_Mask  = 0xF8;
        constexpr uint16_t CHAINID_Shift = 3;
    }

	constexpr int ORCA_REG_SIZE = 973;

} // namespace ORCAReg

#endif // ORCA_REGISTERS_HPP
