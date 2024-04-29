import { Component } from '@angular/core';
import {DataService} from "../services/data.service";
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-folder-upload',
  templateUrl: './folder-upload.component.html',
  styleUrls: ['./folder-upload.component.css']
})
export class FolderUploadComponent {

  selectedFolder: any;
  isFolderValid = false;

  constructor(private uploadService: DataService, private toastrService: ToastrService) { }

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

  onUpload(): void {
    if (this.selectedFolder) {
      // Here, you can implement the folder upload logic
      console.log('Folder uploaded:', this.selectedFolder);
      this.uploadService.uploadFile(this.selectedFolder).subscribe({
        next: (res) => {
          console.log('File uploaded successfully:', res);
        },
        error: (err) => {
          console.error('Error uploading file:', err);
        }
      });

    } else {
      console.log('No folder selected');
    }
  }
}
