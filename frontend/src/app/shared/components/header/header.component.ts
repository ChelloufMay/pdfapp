import { Component, EventEmitter, Output, Input } from '@angular/core';
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
  @Input() dates: string[] = [];
  @Input() types: string[] = [];
  selectedDate = '';
  selectedType = '';
  query = '';

  @Output() search = new EventEmitter<string>();
  @Output() filterChanged = new EventEmitter<{date:string,type:string}>();
  @Output() uploadedEvent = new EventEmitter<void>();

  title = 'PDFExtractor';

  onSearch() { this.search.emit(this.query?.trim()); }
  onFilterChange(){ this.filterChanged.emit({date:this.selectedDate, type:this.selectedType}); }
  // restore Upload button behavior: when upload child emits, forward to parent
  onUploaded(){ this.uploadedEvent.emit(); }
}
