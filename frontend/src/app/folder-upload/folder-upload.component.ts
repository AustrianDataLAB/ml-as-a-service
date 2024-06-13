import {Component} from '@angular/core';
import {DataService} from "../services/data.service";
import {ToastrService} from 'ngx-toastr';

@Component({
  selector: 'app-folder-upload',
  templateUrl: './folder-upload.component.html',
  styleUrls: ['./folder-upload.component.css']
})
export class FolderUploadComponent {

  selectedFolder: any;
  isFolderValid = false;
  isUploadSuccessfull = false;
  isServingStarted = false;
  imageUrl: string | ArrayBuffer | null = null;
  isImageValid = false;
  labelVisible = false;
  classificationLabel = '';
  uploadedImage: any;
  isTrainingFinished = false;
  isTrainingRunning = false;
  servingId: number = 0;

  constructor(private uploadService: DataService, private toastrService: ToastrService) {
  }

  onFolderSelected(event: Event): void {
    this.isFolderValid = false;
    const target = event.target as HTMLInputElement;
    const file: File = (target.files as FileList)[0];

    if (file) {
      if (file.type !== 'application/zip') {
        console.error('Invalid file type. Please upload a zip file.');
        this.toastrService.error('Invalid file type. Please upload a zip file.');
        return;
      }

      if (file.size > 1e9) { // 1e9 bytes = 1GB
        console.error('File is too large. Please upload a file under 1GB.');
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
        console.error('Invalid file type. Please upload a jpeg file.');
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
      console.log('Folder uploaded:', this.selectedFolder);
      this.uploadService.uploadFile(this.selectedFolder).subscribe({
        next: (res) => {
          this.toastrService.success('Folder uploaded successfully.');
          console.log('File uploaded successfully:', res);
          this.isUploadSuccessfull = true;
        },
        error: (err) => {
          this.toastrService.error('Error uploading file. Please try again.');
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
          const id = res.id;

          this.isTrainingFinished = false;
          this.isTrainingRunning= true;
          this.isUploadSuccessfull = false;
          this.isFolderValid = false;
          console.log(this.isTrainingRunning)
          console.log(this.isFolderValid)
          this.toastrService.success('Training started successfully.');
          this.pollStatus(id);
        },
        error: (err) => {
          this.toastrService.error('Error starting training. Please try again.');
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
          this.isTrainingFinished = true;
          this.isTrainingRunning = false;
          this.toastrService.success('Training finished successfully.');
        } else if(res.status === 'Failed') {
          this.isTrainingRunning = false;
          this.toastrService.error('Training failed. Please try again.');
        } else {
          setTimeout(() => this.pollStatus(id), 5000);
        }
      },
      error: (err) => {
        this.toastrService.error('Error getting training status. Please try again.');
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
        this.isServingStarted = true;
      },
      error: (err) => {
        this.toastrService.error('Error starting serving. Please try again.');
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
          this.reset()
        },
        error: (err) => {
          this.toastrService.error('Error stopping serving. Please try again.');
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
          this.toastrService.error('Error uploading file. Please try again.');
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


}