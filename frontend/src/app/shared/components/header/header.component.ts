// src/app/shared/components/header/header.component.ts
import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UploadDialogComponent } from '../upload-dialog/upload-dialog.component';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, FormsModule, UploadDialogComponent],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {
  title = 'DocuVault';
  query = '';

  @Output() search = new EventEmitter<string>();
  @Output() uploadedEvent = new EventEmitter<void>();

  onSearch() {
    this.search.emit(this.query?.trim());
  }

  // forward event when upload completes
  onUploaded() {
    this.uploadedEvent.emit();
  }
}
