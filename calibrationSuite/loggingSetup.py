##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import logging


def setupScriptLogging(fileName, logLevel):
    # setup logging to file '<filename>.log', and configures the underlying calibration-library logging.
    # log file gets appended to each new run, and can manually delete for fresh log.
    logger = logging.getLogger()
    logger.setLevel(logLevel)

    # create handlers
    file_handler = logging.FileHandler(fileName)
    print_handler = logging.StreamHandler()

    # Set log level for handlers
    file_handler.setLevel(logLevel)
    print_handler.setLevel(logLevel)

    # Create formatters and add them to handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    print_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(print_handler)
    
    logging.basicConfig(
        filename=fileName,
        level=logLevel,  # For full logging set to INFO which includes ERROR logging too
        format="%(asctime)s - %(levelname)s - %(message)s",  # levelname is log severity (ERROR, INFO, etc)
    )
