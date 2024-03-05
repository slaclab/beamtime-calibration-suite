import logging


def setupScriptLogging(fileName, logLevel):
    # Setup logging to file '<filename>.log', and configures the underlying calibration-library logging.
    # Log file gets appended to each new run, and can manually delete for fresh log.
    # (Could change so makes new unique log each run or overwrites existing log)
    logging.basicConfig(
        filename=fileName,
        level=logLevel,  # For full logging set to INFO which includes ERROR logging too
        format="%(asctime)s - %(levelname)s - %(message)s",  # levelname is log severity (ERROR, INFO, etc)
    )
