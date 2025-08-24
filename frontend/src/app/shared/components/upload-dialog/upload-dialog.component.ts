// upload-dialog.component.ts
// Handles picking a file and uploading it with progress indicator.
// Emits (uploaded) when upload completes successfully.
import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { finalize } from 'rxjs';
import { HttpEventType, HttpEvent } from '@angular/common/http';
import { DocumentService } from '../../../core/services/document.service';

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

  onFilePicked(e: Event | any) {
    const f = e?.target?.files && e.target.files[0];
    if (f) this.selected = f;
    else this.selected = undefined;
  }

  // Use uploadWithProgress to show progress events
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
      next: (event: HttpEvent<any>) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          this.uploadProgress = Math.round(100 * (event.loaded / event.total));
        }
        if (event.type === HttpEventType.Response) {
          // Upload finished successfully
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


