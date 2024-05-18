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

  constructor(private uploadService: DataService, private toastrService: ToastrService) {
  }

  onFolderSelected(event: Event): void {
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
        this.toastrService.error('Invalid file type. Please upload a jpeg file.');
        return;
      }

      if (file.size > 1e6) { // 1e6 bytes = 1MB
        console.error('File is too large. Please upload a file under 1MB.');
        this.toastrService.error('File is too large. Please upload a file under 1MB.');
        return;
      }
      this.isImageValid = true;
      this.uploadedImage = file;

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

  classify(): void {
    if (this.isImageValid) {
      this.uploadService.classify(this.uploadedImage).subscribe({
        next: (res) => {
          this.labelVisible = true;
          this.isUploadSuccessfull = true;
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

  startTraining(): void {
    if (this.isUploadSuccessfull) {
      console.log('Start training');
      this.uploadService.startTraining().subscribe({
        next: (res) => {
          this.toastrService.success('Started training successfully.');
        },
        error: (err) => {
          this.toastrService.error('Error starting training. Please try again.');
          console.error('Error uploading file:', err);
        }
      });

    }
  }

  startServing(): void {
    console.log('Start serving');
    this.uploadService.startServing().subscribe({
      next: (res) => {
        this.toastrService.success('Started serving successfully.');
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
          this.isServingStarted = false;
        },
        error: (err) => {
          this.toastrService.error('Error stopping serving. Please try again.');
          console.error('Error stopping serving:', err);
        }
      });
    }
  }


}
