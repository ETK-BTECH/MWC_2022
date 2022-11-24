from Sequencers_DC import LED_sequencer_step
from settings import *

LED_sequencies = (
    # Sequence 0 : only position lights
    ( LED_sequencer_step (
        LED_Colors = (
            ( ldFL, 60, 0, 0 ),
            ( ldFR, 0, 60, 0 ),
            ( ldRL, 30, 30, 30 ),
            ( ldRR, 30, 30, 30 ),
            ( ldBFR, 0, 0, 0 ),
            ( ldBFL, 0, 0, 0 ),
            ( ldBFR, 0, 0, 0 ),
            ( ldBRR, 0, 0, 0) ),
        Duration = 0)
    ),
    # Sequence 1 : position lights and red beacon
    (
        LED_sequencer_step (
            LED_Colors = (
                ( ldFL, 60, 0, 0 ),
                ( ldFR, 0, 60, 0 ),
                ( ldRL, 30, 30, 30 ),
                ( ldRR, 30, 30, 30 ),
                ( ldBFR, 0, 0, 0 ),
                ( ldBFL, 0, 0, 0 ),
                ( ldBFR, 0, 0, 0 ),
                ( ldBRR, 0, 0, 0) ),
            Duration = 500),
        LED_sequencer_step (
            LED_Colors = (
                ( ldBFR, 255, 0, 0 ),
                ( ldBFL, 255, 0, 0 ),
                ( ldBRR, 255, 0, 0 ),
                ( ldBRL, 255, 0, 0) ),
            Duration = 100),
        LED_sequencer_step (
            LED_Colors = (
                ( ldBFR, 0, 0, 0 ),
                ( ldBFL, 0, 0, 0 ),
                ( ldBRR, 0, 0, 0 ),
                ( ldBRL, 0, 0, 0) ),
            Duration = 400)
    ),
    # Sequence 2 : position lights, red beacon and strobes
    (
        LED_sequencer_step (
            LED_Colors = (
                ( ldFL, 60, 0, 0 ),
                ( ldFR, 0, 60, 0 ),
                ( ldRL, 255, 255, 255 ),
                ( ldRR, 255, 255, 255 ),
                ( ldBFR, 255, 255, 255 ),
                ( ldBFL, 255, 255, 255 ),
                ( ldBRR, 255, 255, 255 ),
                ( ldBRL, 255, 255, 255) ),
            Duration = 50),
        LED_sequencer_step (
            LED_Colors = (
                ( ldBFR, 0, 0, 0 ),
                ( ldBFL, 0, 0, 0 ),
                ( ldBRR, 0, 0, 0 ),
                ( ldBRL, 0, 0, 0) ),
            Duration = 50),
        LED_sequencer_step (
            LED_Colors = (
                ( ldRL, 20, 20, 20 ),
                ( ldRR, 20, 20, 20 ),
                ( ldBFR, 255, 255, 255 ),
                ( ldBFL, 255, 255, 255 ),
                ( ldBRR, 255, 255, 255 ),
                ( ldBRL, 255, 255, 255) ),
            Duration = 50),
        LED_sequencer_step (
            LED_Colors = (
                ( ldBFR, 0, 0, 0 ),
                ( ldBFL, 0, 0, 0 ),
                ( ldBRR, 0, 0, 0 ),
                ( ldBRL, 0, 0, 0) ),
            Duration = 350),
        LED_sequencer_step (
            LED_Colors = (
                ( ldBFR, 255, 0, 0 ),
                ( ldBFL, 255, 0, 0 ),
                ( ldBRR, 255, 0, 0 ),
                ( ldBRL, 255, 0, 0) ),
            Duration = 100),
        LED_sequencer_step (
            LED_Colors = (
                ( ldBFR, 0, 0, 0 ),
                ( ldBFL, 0, 0, 0 ),
                ( ldBRR, 0, 0, 0 ),
                ( ldBRL, 0, 0, 0) ),
            Duration = 400)
    )
)
            
          
      

