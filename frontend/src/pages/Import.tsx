import { useState } from 'react';
import {
  Container,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Box,
  Typography,
  Button,
} from '@mui/material';
import FileUpload from '../components/import/FileUpload';
import DataPreview from '../components/import/DataPreview';
import ColumnMapper from '../components/import/ColumnMapper';
import ValidationResults from '../components/import/ValidationResults';
import ImportProgress from '../components/import/ImportProgress';
import { DataType, ColumnMapping } from '../types/import';

const steps = [
  'Upload File',
  'Preview Data',
  'Map Columns',
  'Validate',
  'Process',
  'Results',
];

export default function Import() {
  const [activeStep, setActiveStep] = useState(0);
  const [jobId, setJobId] = useState<string>('');
  const [dataType, setDataType] = useState<DataType>('farms_plots');
  const [columnMappings, setColumnMappings] = useState<ColumnMapping[]>([]);
  const [skipInvalidRows, setSkipInvalidRows] = useState(false);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setJobId('');
    setColumnMappings([]);
    setSkipInvalidRows(false);
  };

  const handleUploadComplete = (uploadedJobId: string, uploadedDataType: DataType) => {
    setJobId(uploadedJobId);
    setDataType(uploadedDataType);
    handleNext();
  };

  const handlePreviewComplete = () => {
    handleNext();
  };

  const handleMappingComplete = (mappings: ColumnMapping[]) => {
    setColumnMappings(mappings);
    handleNext();
  };

  const handleValidationComplete = (skipInvalid: boolean) => {
    setSkipInvalidRows(skipInvalid);
    handleNext();
  };

  const handleImportComplete = () => {
    // Import is complete, show results
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <FileUpload
            onUploadComplete={handleUploadComplete}
            onBack={handleBack}
          />
        );
      case 1:
        return (
          <DataPreview
            jobId={jobId}
            onNext={handlePreviewComplete}
            onBack={handleBack}
          />
        );
      case 2:
        return (
          <ColumnMapper
            jobId={jobId}
            dataType={dataType}
            onNext={handleMappingComplete}
            onBack={handleBack}
          />
        );
      case 3:
        return (
          <ValidationResults
            jobId={jobId}
            dataType={dataType}
            columnMappings={columnMappings}
            onNext={handleValidationComplete}
            onBack={handleBack}
          />
        );
      case 4:
      case 5:
        return (
          <ImportProgress
            jobId={jobId}
            columnMappings={columnMappings}
            skipInvalidRows={skipInvalidRows}
            onComplete={handleImportComplete}
            onReset={handleReset}
          />
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Import Data
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Import farm data from CSV or Excel files through our guided wizard
          </Typography>
        </Box>

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label, index) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box sx={{ minHeight: 400 }}>
          {getStepContent(activeStep)}
        </Box>

        {activeStep === steps.length && (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              All steps completed - Import finished!
            </Typography>
            <Button onClick={handleReset} sx={{ mt: 2 }}>
              Start New Import
            </Button>
          </Box>
        )}
      </Paper>
    </Container>
  );
}
