import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentService } from '../../../core/services/document.service';
import { finalize } from 'rxjs';

@Component({
  selector: 'app-upload-dialog',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload-dialog.component.html',
  styleUrls: ['./upload-dialog.component.scss']
})
export class UploadDialogComponent {
  selected?: File;
  uploading = false;
  uploadProgress = 0;

  @Output() uploaded = new EventEmitter<void>();

  constructor(private svc: DocumentService) {}

  onFilePicked(e: any) {
    const f = e?.target?.files && e.target.files[0];
    if (f) this.selected = f;
    else this.selected = undefined;
  }

  upload() {
    if (!this.selected || this.uploading) return;

    this.uploading = true;
    this.uploadProgress = 0;

    this.svc.uploadWithProgress(this.selected).pipe(
      finalize(() => {
        this.uploading = false;
        this.uploadProgress = 0;
      })
    ).subscribe({
      next: (event: any) => {
        // handle progress and final response
        if (event.type === 1 && event.total) { // UploadProgress
          this.uploadProgress = Math.round(100 * (event.loaded / event.total));
        } else if (event.type === 4) { // Response
          this.selected = undefined;
          this.uploaded.emit();
        }
      },
      error: (err) => {
        console.error('Upload failed', err);
        alert('Upload failed: ' + (err?.statusText || err?.message || 'unknown'));
      }
    });
  }
}



