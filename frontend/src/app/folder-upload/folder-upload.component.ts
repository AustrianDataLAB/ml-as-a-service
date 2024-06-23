import {Component, OnInit} from '@angular/core';
import {DataService} from "../services/data.service";
import {ToastrService} from 'ngx-toastr';

@Component({
  selector: 'app-folder-upload',
  templateUrl: './folder-upload.component.html',
  styleUrls: ['./folder-upload.component.css']
})
export class FolderUploadComponent implements OnInit{

  selectedFolder: any;
  isFolderValid = false;
  isUploadSuccessfull = false;
  isServingStarted = false;
  imageUrl: string | ArrayBuffer | null = null;
  isImageValid = false;
  labelVisible = false;
  classificationLabel = '';
  uploadedImage: any;
  isTrainingRunning = false;
  servingId: number = 0;
  trainingId: number = 0;
  isLoading = false;

  constructor(private uploadService: DataService, private toastrService: ToastrService) {
  }

  ngOnInit(): void {
    this.isTrainingRunning = localStorage.getItem('isTrainingRunning') === 'true';
    this.trainingId = Number(localStorage.getItem('trainingId'));
    if(this.isTrainingRunning){
      this.pollStatus(this.trainingId);
    }
    this.isServingStarted = localStorage.getItem('isServingStarted') === 'true';
  }

  onFolderSelected(event: Event): void {
    this.isFolderValid = false;
    const target = event.target as HTMLInputElement;
    const file: File = (target.files as FileList)[0];

    if (file) {
      console.log("file type:" + file.type)
      if (file.type !== 'application/zip' && file.type !== 'application/x-zip-compressed') {
        console.error('Invalid file type. Please upload a zip file.');
        this.toastrService.error('Invalid file type. Please upload a zip file.');
        return;
      }

      if (file.size > 1e9) { // 1e9 bytes = 1GB
        console.error('File is too large. Please upload a file under 1GB.');
        this.toastrService.error('File is too large. Please upload a file under 1GB.');

        return;
      }
      this.isFolderValid = true;
      this.selectedFolder = file;
    }
  }

  onImageSelected(event: Event): void {
    const target = event.target as HTMLInputElement;
    const file: File = (target.files as FileList)[0];

    if (file) {
      if (file.type !== 'image/jpeg'  && file.type !== 'image/png') {
        console.error('Invalid file type. Please upload a jpeg or png file.');
        this.toastrService.error('Invalid file type. Please upload a jpeg or png file.');
        return;
      }

      if (file.size > 1e6) { // 1e6 bytes = 1MB
        console.error('File is too large. Please upload a file under 1MB.');
        this.toastrService.error('File is too large. Please upload a file under 1MB.');
        return;
      }
      this.isImageValid = true;
      this.uploadedImage = file;
      this.classificationLabel = '';

      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        this.imageUrl = reader.result;
      };
    }
  }

  onUpload(): void {
    if (this.selectedFolder) {
      this.isLoading = true;
      console.log('Folder uploaded:', this.selectedFolder);
      this.uploadService.uploadFile(this.selectedFolder).subscribe({
        next: (res) => {
          this.toastrService.success('Folder uploaded successfully.');
          console.log('File uploaded successfully:', res);
          this.isLoading = false;
          this.isUploadSuccessfull = true;
        },
        error: (err) => {
          this.isLoading = false;
          this.printErrorMessage(err)
          console.error('Error uploading file:', err);
        }
      });

    } else {
      console.log('No folder selected');
    }
  }

  startTraining(): void {
    if (this.isUploadSuccessfull) {
      console.log('Start training');
      this.uploadService.startTraining().subscribe({
        next: (res) => {
          this.trainingId = res.id;
          localStorage.setItem('isTrainingRunning', 'true');
          localStorage.setItem('trainingId', this.trainingId.toString());
          this.isTrainingRunning= true;
          this.isUploadSuccessfull = false;
          this.isFolderValid = false;
          console.log(this.isTrainingRunning)
          console.log(this.isFolderValid)
          this.toastrService.success('Training started successfully.');
          this.pollStatus(this.trainingId);
        },
        error: (err) => {
          this.printErrorMessage(err)
          console.error('Error uploading file:', err);
        }
      });

    }
  }

  pollStatus(id: number): void {
    this.uploadService.getTrainingStatus(id).subscribe({
      next: (res) => {
        console.log('Training status:', res);
        if (res.status === 'Succeeded') {
          this.isTrainingRunning = false;
          localStorage.setItem('isTrainingRunning', 'false');
          this.toastrService.success('Training finished successfully.');
        } else if(res.status === 'Failed') {
          this.isTrainingRunning = false;
          this.toastrService.error('Training failed. Please try again.');
        } else {
          setTimeout(() => this.pollStatus(id), 5000);
        }
      },
      error: (err) => {
        this.printErrorMessage(err)
        console.error('Error getting training status:', err);
      }
    });
  }

  startServing(): void {
    console.log('Start serving');
    this.uploadService.startServing().subscribe({
      next: (res) => {
        this.toastrService.success('Serving started successfully.');
        this.servingId = res.id;
        localStorage.setItem('isServingStarted', 'true');
        this.isServingStarted = true;
      },
      error: (err) => {
        this.printErrorMessage(err)
        console.error('Error starting serving:', err);
      }
    });

  }

  stopServing(): void {
    console.log('Stop serving');
    if (this.isServingStarted) {
      this.uploadService.stopServing().subscribe({
        next: (res) => {
          this.toastrService.success('Stopped serving successfully.');
          localStorage.setItem('isServingStarted', 'false');
          this.reset()
        },
        error: (err) => {
          this.printErrorMessage(err)
          console.error('Error stopping serving:', err);
        }
      });
    }
  }

  classify(): void {
    if (this.isImageValid) {
      this.uploadService.classify(this.uploadedImage, this.servingId).subscribe({
        next: (res) => {
          this.labelVisible = true;
          this.classificationLabel = res;
        },
        error: (err) => {
          this.printErrorMessage(err)
          console.error('Error uploading file:', err);
        }
      });

    } else {
      console.log('No folder selected');
    }
  }


  reset():void{
    this.isServingStarted = false;
    this.imageUrl = null;
    this.isImageValid = false;
    this.labelVisible = false;
    this.classificationLabel = '';
    this.uploadedImage = null;
  }


  printErrorMessage(error: any): void {
    let errorMessage = undefined
    let unknownErrorMessage = 'An error has occurred. Please try again later.'
    if (error.error && error.error.error) {
      errorMessage = error.error.error;
    } else if (error.message) {
      errorMessage = error.message;
    }

    this.toastrService.error(errorMessage ?? unknownErrorMessage);

  }

}
