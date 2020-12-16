/******************************************************************************
  * \attention
  *
  * <h2><center>&copy; COPYRIGHT 2019 STMicroelectronics</center></h2>
  *
  * Licensed under ST MYLIBERTY SOFTWARE LICENSE AGREEMENT (the "License");
  * You may not use this file except in compliance with the License.
  * You may obtain a copy of the License at:
  *
  *        www.st.com/myliberty
  *
  * Unless required by applicable law or agreed to in writing, software 
  * distributed under the License is distributed on an "AS IS" BASIS, 
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied,
  * AND SPECIFICALLY DISCLAIMING THE IMPLIED WARRANTIES OF MERCHANTABILITY,
  * FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
  * See the License for the specific language governing permissions and
  * limitations under the License.
  *
******************************************************************************/
/*! \file   ndef_demo.c
 *
 *  \author Jiamin Wang
 *
 *  \brief Demo application
 *
 *  This was originally a demo filed that showed how to poll for different types
 *  of NFC cards/devices, and how to exchange data with devices using the RFAL
 *  library. This file has been edited now to only support the reading of Type 4
 *  and Type 5 tags, more specifically the NFCA Passive ISO-DEP and
 *  ISO15693/NFC-V cards.
 * 
 */
 
/*
 ******************************************************************************
 * INCLUDES
 ******************************************************************************
 */
#include "demo.h"
#include "utils.h"
#include "rfal_nfc.h"
#include "ndef_poller.h"
#include "ndef_t2t.h"
#include "ndef_t4t.h"
#include "ndef_t5t.h"
#include "ndef_message.h"
#include "ndef_types_rtd.h"
#include "ndef_dump.h"
/*
******************************************************************************
* GLOBAL DEFINES
******************************************************************************
*/

/* Definition of possible states the demo state machine could have */
#define DEMO_ST_NOTINIT               0  /*!< Demo State:  Not initialized */
#define DEMO_ST_START_DISCOVERY       1  /*!< Demo State:  Start Discovery */
#define DEMO_ST_DISCOVERY             2  /*!< Demo State:  Discovery       */

#define NDEF_DEMO_READ                0U   /*!< NDEF menu read             */
#define NDEF_DEMO_FORMAT_TAG          3U   /*!< NDEF menu format tag       */
#define NDEF_DEMO_MAX_FEATURES        1U   /*!< Number of menu items       */
#define NDEF_LED_BLINK_DURATION       250U /*!< Led blink duration         */ 
#define DEMO_RAW_MESSAGE_BUF_LEN      8192 /*!< Raw message buffer len     */
#define DEMO_ST_MANUFACTURER_ID       0x02U /*!< ST Manufacturer ID        */

/*
 ******************************************************************************
 * LOCAL VARIABLES
 ******************************************************************************
 */

/* P2P communication data */
static uint8_t NFCID3[] = {0x01, 0xFE, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A};
static uint8_t GB[] = {0x46, 0x66, 0x6d, 0x01, 0x01, 0x11, 0x02, 0x02, 0x07, 0x80, 0x03, 0x02, 0x00, 0x03, 0x04, 0x01, 0x32, 0x07, 0x01, 0x03};
    
#if defined(ST25R3916) && defined(RFAL_FEATURE_LISTEN_MODE)
/* NFC-A CE config */
static uint8_t ceNFCA_NFCID[]     = {0x02, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66};                   /* NFCID / UID (7 bytes)                    */
static uint8_t ceNFCA_SENS_RES[]  = {0x44, 0x00};                                                 /* SENS_RES / ATQA                          */
static uint8_t ceNFCA_SEL_RES     = 0x20;                                                         /* SEL_RES / SAK                            */

/* NFC-F CE config */
static uint8_t ceNFCF_nfcid2[]     = {0x02, 0xFE, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66};
static uint8_t ceNFCF_SC[]         = {0x12, 0xFC};
static uint8_t ceNFCF_SENSF_RES[]  = {0x01,                                                       /* SENSF_RES                                */
                                      0x02, 0xFE, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66,             /* NFCID2                                   */
                                      0x00, 0x00, 0x00, 0x00, 0x00, 0x7F, 0x7F, 0x00,             /* PAD0, PAD01, MRTIcheck, MRTIupdate, PAD2 */
                                      0x00, 0x00 };                                               /* RD                                       */
#endif /* RFAL_FEATURE_LISTEN_MODE */


static const uint8_t *ndefDemoFeatureDescription[NDEF_DEMO_MAX_FEATURES] =
{
    (uint8_t *)"Tap a tag to read its content"
};

 
/*
 ******************************************************************************
 * LOCAL VARIABLES
 ******************************************************************************
 */

static rfalNfcDiscoverParam discParam;
static uint8_t              state = DEMO_ST_NOTINIT;

static uint8_t              ndefDemoFeature     = NDEF_DEMO_READ;
static uint8_t              ndefDemoPrevFeature = 0xFF;
static bool                 verbose             = false;

static uint32_t             timer;

/*
******************************************************************************
* LOCAL FUNCTION PROTOTYPES
******************************************************************************
*/


ReturnCode  demoTransceiveBlocking( uint8_t *txBuf, uint16_t txBufSize, uint8_t **rxBuf, uint16_t **rcvLen, uint32_t fwt );


/*!
 *****************************************************************************
 * \brief Demo Ini
 *
 *  This function Initializes the required layers for the demo
 *
 * \return true  : Initialization ok
 * \return false : Initialization failed
 *****************************************************************************
 */
bool demoIni( void )
{
	ReturnCode err;

#if defined(STM32L476xx)
    if( (CoreDebug->DHCSR & CoreDebug_DHCSR_C_DEBUGEN_Msk) != 0)
    {
        verbose = true;
    }
#endif
    
    err = rfalNfcInitialize();
    if( err == ERR_NONE )
    {
        discParam.compMode      = RFAL_COMPLIANCE_MODE_NFC;
        discParam.devLimit      = 1U;
        discParam.nfcfBR        = RFAL_BR_212;
        discParam.ap2pBR        = RFAL_BR_424;

        ST_MEMCPY( &discParam.nfcid3, NFCID3, sizeof(NFCID3) );
        ST_MEMCPY( &discParam.GB, GB, sizeof(GB) );
        discParam.GBLen         = sizeof(GB);

        discParam.notifyCb             = NULL;
        discParam.totalDuration        = 1000U;
        discParam.wakeupEnabled        = false;
        discParam.wakeupConfigDefault  = true;
        discParam.techs2Find           = ( RFAL_NFC_POLL_TECH_A | RFAL_NFC_POLL_TECH_B | RFAL_NFC_POLL_TECH_F | RFAL_NFC_POLL_TECH_V | RFAL_NFC_POLL_TECH_ST25TB );
#if defined(ST25R3911) || defined(ST25R3916)
        discParam.techs2Find   |= RFAL_NFC_POLL_TECH_AP2P;
#endif /* ST25R3911 || ST25R3916 */
        
        
#if defined(ST25R3916)
      
      /* Set configuration for NFC-A CE */
      ST_MEMCPY( discParam.lmConfigPA.SENS_RES, ceNFCA_SENS_RES, RFAL_LM_SENS_RES_LEN );                        /* Set SENS_RES / ATQA */
      ST_MEMCPY( discParam.lmConfigPA.nfcid, ceNFCA_NFCID, RFAL_NFCID2_LEN );                                   /* Set NFCID / UID */
      discParam.lmConfigPA.nfcidLen = RFAL_LM_NFCID_LEN_07;                                                     /* Set NFCID length to 7 bytes */
      discParam.lmConfigPA.SEL_RES  = ceNFCA_SEL_RES;                                                           /* Set SEL_RES / SAK */

      /* Set configuration for NFC-F CE */
      ST_MEMCPY( discParam.lmConfigPF.SC, ceNFCF_SC, RFAL_LM_SENSF_SC_LEN );                                    /* Set System Code */
      ST_MEMCPY( &ceNFCF_SENSF_RES[RFAL_NFCF_LENGTH_LEN], ceNFCF_nfcid2, RFAL_LM_SENSF_RES_LEN );               /* Load NFCID2 on SENSF_RES */
      ST_MEMCPY( discParam.lmConfigPF.SENSF_RES, ceNFCF_SENSF_RES, RFAL_LM_SENSF_RES_LEN );                     /* Set SENSF_RES / Poll Response */
      
      discParam.techs2Find |= ( RFAL_NFC_LISTEN_TECH_A | RFAL_NFC_LISTEN_TECH_F );
      
#endif /* ST25R3916 */

        state = DEMO_ST_START_DISCOVERY;
        return true;
    }
    return false;
}

/*!
 *****************************************************************************
 * \brief Demo Cycle
 *
 *  This function executes the demo state machine. 
 *  It must be called periodically
 *****************************************************************************
 */


void demoCycle( void )
{
	static rfalNfcDevice *nfcDevice;

    rfalNfcaSensRes       sensRes;
    rfalNfcaSelRes        selRes;
    

    rfalNfcvInventoryRes  invRes;
    uint16_t              rcvdLen;
    
    rfalNfcWorker();                                    /* Run RFAL worker periodically */
    
    if( (ndefDemoFeature != NDEF_DEMO_READ) && (platformTimerIsExpired(timer)) )
    {
        platformLog("Timer expired, back to Read mode...\r\n");
        ndefDemoFeature = NDEF_DEMO_READ;
    }
    
    if( ndefDemoFeature != ndefDemoPrevFeature )
    {
        ndefDemoPrevFeature = ndefDemoFeature;
        platformLog("%s\r\n", ndefDemoFeatureDescription[ndefDemoFeature]);
    }
    

    switch( state )
    {
        /*******************************************************************************/
        case DEMO_ST_START_DISCOVERY:

    
            rfalNfcDeactivate( false );
            rfalNfcDiscover( &discParam );

            state = DEMO_ST_DISCOVERY;
            break;

        /*******************************************************************************/
        case DEMO_ST_DISCOVERY:
            if( rfalNfcIsDevActivated(rfalNfcGetState()))
            {
            	platformLog("tag detected :)\r\n");
                rfalNfcGetActiveDevice( &nfcDevice );
                

                platformDelay(50);
                ndefDemoPrevFeature = 0xFF; /* Force the display of the prompt */
                switch( nfcDevice->type )
                {
                    /*******************************************************************************/
                    case RFAL_NFC_LISTEN_TYPE_NFCA:
                    
                        platformLedOn(PLATFORM_LED_A_PORT, PLATFORM_LED_A_PIN);
                        switch( nfcDevice->dev.nfca.type )
                        {
                            case RFAL_NFCA_T4T: // All tags in ST25TA TAG BAG and ST25TA64K and ST25V02K HC
                                platformLog("NFCA Passive ISO-DEP device found. UID: %s\r\n", hex2Str( nfcDevice->nfcid, nfcDevice->nfcidLen ) );
                                rfalIsoDepDeselect(); 
                                break;

                            default:
                                platformLog("ISO14443A/NFC-A card found. UID: %s\r\n", hex2Str( nfcDevice->nfcid, nfcDevice->nfcidLen ) );
                                rfalNfcaPollerSleep();
                                break;
                        }
                        /* Loop until tag is removed from the field */
                        platformLog("Operation completed. Tag can be removed from the field\r\n\n");
                        platformLedOff(PLATFORM_LED_A_PORT, PLATFORM_LED_A_PIN);

                        // prep string for i2c send
                        strUID = hex2Str(nfcDevice->nfcid, RFAL_NFCV_UID_LEN);
                        haveUID = 1;

                    	// platformLog print the strUID and convert it to a buffer here
                    	platformLog("SCANNED: strUID = %s\r\n", strUID);
                    	for (int i=0; i<16; i++){
                        	// store i2cData[i] = strUID[i]
                    		if (i<8){
                    			i2cDataBuf[i] = strUID[i];
                    		}
                    		else{
                    			i2cDataBuf[i] = strUID[i-8];
                    		}
                    	}

                        rfalNfcaPollerInitialize();
                        while( rfalNfcaPollerCheckPresence(RFAL_14443A_SHORTFRAME_CMD_WUPA, &sensRes) == ERR_NONE )
                        {
                            if( ((nfcDevice->dev.nfca.type == RFAL_NFCA_T1T) && (!rfalNfcaIsSensResT1T(&sensRes ))) ||
                                ((nfcDevice->dev.nfca.type != RFAL_NFCA_T1T) && (rfalNfcaPollerSelect(nfcDevice->dev.nfca.nfcId1, nfcDevice->dev.nfca.nfcId1Len, &selRes) != ERR_NONE)) )
                            {
                                break;
                            }
                            rfalNfcaPollerSleep();
                            platformDelay(130);
                        }
                        break;
                    
                    /*******************************************************************************/
                    case RFAL_NFC_LISTEN_TYPE_NFCV: //ST25TV02K and ST25TV512
                        {
                            uint8_t devUID[RFAL_NFCV_UID_LEN];
                            
                            ST_MEMCPY( devUID, nfcDevice->nfcid, nfcDevice->nfcidLen );   /* Copy the UID into local var */
                            REVERSE_BYTES( devUID, RFAL_NFCV_UID_LEN );                   /* Reverse the UID for display purposes */
                            platformLog("ISO15693/NFC-V card found. UID: %s\r\n", hex2Str(devUID, RFAL_NFCV_UID_LEN));

                            platformLedOn(PLATFORM_LED_V_PORT, PLATFORM_LED_V_PIN);

                            /* Loop until tag is removed from the field */
                            platformLog("Operation completed. Tag can be removed from the field\r\n\n");
                            platformLedOff(PLATFORM_LED_V_PORT, PLATFORM_LED_V_PIN);

                            /*
                            // prep string for i2c send
                            strUID = hex2Str(devUID, RFAL_NFCV_UID_LEN);
                            haveUID = 1;

                        	// platformLog print the strUID and convert it to a buffer here
                        	platformLog("SCANNED: strUID = %s\r\n", strUID);
                        	for (int i=0; i<16; i++){
                            	// store i2cData[i] = strUID[i]
                        		i2cDataBuf[i] = strUID[i];
                        	}
                        	*/

                            rfalNfcvPollerInitialize();
                            while (rfalNfcvPollerInventory( RFAL_NFCV_NUM_SLOTS_1, RFAL_NFCV_UID_LEN * 8U, nfcDevice->dev.nfcv.InvRes.UID, &invRes, &rcvdLen) == ERR_NONE)
                            {
                                platformDelay(130);
                            }
                        }
                        break;
                        
                    default:
                        break;
                }
                
                rfalNfcDeactivate( false );
                platformDelay( 500 );
                state = DEMO_ST_START_DISCOVERY;
            }
            else {
            	platformLog("no tag detected\r\n");
            }
            break;

        /*******************************************************************************/
        case DEMO_ST_NOTINIT:
        default:
            break;
    }
}

/*!
 *****************************************************************************
 * \brief Demo Blocking Transceive 
 *
 * Helper function to send data in a blocking manner via the rfalNfc module 
 *  
 * \warning A protocol transceive handles long timeouts (several seconds), 
 * transmission errors and retransmissions which may lead to a long period of 
 * time where the MCU/CPU is blocked in this method.
 * This is a demo implementation, for a non-blocking usage example please 
 * refer to the Examples available with RFAL
 *
 * \param[in]  txBuf      : data to be transmitted
 * \param[in]  txBufSize  : size of the data to be transmited
 * \param[out] rxData     : location where the received data has been placed
 * \param[out] rcvLen     : number of data bytes received
 * \param[in]  fwt        : FWT to be used (only for RF frame interface, 
 *                                          otherwise use RFAL_FWT_NONE)
 *
 * 
 *  \return ERR_PARAM     : Invalid parameters
 *  \return ERR_TIMEOUT   : Timeout error
 *  \return ERR_FRAMING   : Framing error detected
 *  \return ERR_PROTO     : Protocol error detected
 *  \return ERR_NONE      : No error, activation successful
 * 
 *****************************************************************************
 */
ReturnCode demoTransceiveBlocking( uint8_t *txBuf, uint16_t txBufSize, uint8_t **rxData, uint16_t **rcvLen, uint32_t fwt )
{
    ReturnCode err;
    
    err = rfalNfcDataExchangeStart( txBuf, txBufSize, rxData, rcvLen, fwt );
    if( err == ERR_NONE )
    {
        do{
            rfalNfcWorker();
            err = rfalNfcDataExchangeGetStatus();
        }
        while( err == ERR_BUSY );
    }
    return err;
}


/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
