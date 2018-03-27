#define frontLeftReading frontSensorsCalibrationCM[0]
#define frontRightReading frontSensorsCalibrationCM[1]

#define rightFrontReading sideSensorsCalibrationCM[0]
#define rightBackReading sideSensorsCalibrationCM[1]

//Function Declaration
volatile double* calibrationFrontSensorReading();
volatile double* getFrontCalibrationReading(boolean quick);
double getRightSensorReading();

//Array Declaration
volatile double frontSensorsCalibrationCM[2];
volatile double calibrationFrontSensorRaw[2];

//Front Sensor Values
//Get average reading over a number of samples for front
volatile double* getFrontCalibrationReading(boolean quick) {
  if (quick)
  {
    calibrationFrontSensorRaw[0] = analogRead(frontLeft);
    calibrationFrontSensorRaw[1] = analogRead(frontRight);
  }
  else
  {
    calibrationFrontSensorReading();
  }

  //------------------------------------FRONT RIGHT-----------------------------------------------------
  //y = 5488.9x - 0.4385
  frontSensorsCalibrationCM[1] = 5488.9 * (1 / calibrationFrontSensorRaw[1]) - 0.4385;

  //------------------------------------FRONT LEFT-----------------------------------------------------
  //y = 5410x + 0.3186
  frontSensorsCalibrationCM[0] = 5410 * (1 / calibrationFrontSensorRaw[0]) + 0.3186;

  return frontSensorsCalibrationCM;
}

volatile double* calibrationFrontSensorReading() {
  int size = 70;

  int listOfReadingsFL[size];
  int listOfReadingsFR[size];

  //Get Reading from Sensor
  for (int a = 0; a < size; a++)
  {
    listOfReadingsFL[a] = analogRead(frontLeft);
    listOfReadingsFR[a] = analogRead(frontRight);
    delay(1);
  }

  //Get median averaged from list
  calibrationFrontSensorRaw[0] = sortAndAverage(listOfReadingsFL, size, 3);
  calibrationFrontSensorRaw[1] = sortAndAverage(listOfReadingsFR, size, 3);

  return calibrationFrontSensorRaw;
}

double getRightSensorReading(){
	
	double rightSideReading = analogRead(right);
	
	int size = 50;
	int listOfReadingsRight[size];

	//Get Reading from Sensor
	for (int a = 0; a < size; a++)
	{
		listOfReadingsRight[a] = analogRead(right);
		delay(1);
	}

	//Get median averaged from list
	rightSideReading = sortAndAverage(listOfReadingsRight, size, 3);

	//------------------------------------RIGHT-----------------------------------------------------
	//y = 5236.7x - 0.032
	return (5236.7 / rightSideReading) - 0.032;
}