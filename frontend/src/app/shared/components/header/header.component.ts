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

  // relay upload event from child
  onUploaded() {
    this.uploadedEvent.emit();
  }
}

