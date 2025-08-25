// frontend/src/app/pages/home/home.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DocumentService, DocumentDto } from '../../core/services/document.service';
import { HeaderComponent } from '../../shared/components/header/header.component';
import { FileCardComponent } from '../../shared/components/file-card/file-card.component';
import { DocumentViewerComponent } from '../../shared/components/document-viewer/document-viewer.component';
import { ConfirmDialogComponent } from '../../shared/components/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, HeaderComponent, FileCardComponent, DocumentViewerComponent, ConfirmDialogComponent],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  docs: DocumentDto[] = [];
  pageDocs: DocumentDto[] = [];
  pageIndex = 0;
  pageSize = 12;
  query = '';

  viewerVisible = false;
  viewerDoc?: DocumentDto;

  // filter lists for header
  dates: string[] = [];
  types: string[] = [];

  // confirm dialog state
  confirmVisible = false;
  confirmTargetId: string | null = null;
  confirmTargetName = '';

  // last applied filters to retain context between pages
  appliedDate = '';
  appliedType = '';

  constructor(private svc: DocumentService) {}

  ngOnInit(): void { this.load(); }

  load(): void {
    this.svc.list().subscribe({
      next: (ds) => {
        this.docs = Array.isArray(ds) ? ds : [];
        this.populateFilterLists();
        this.pageIndex = 0;
        this.applyFilters();
      },
      error: (err) => { console.error(err); this.docs = []; }
    });
  }

  populateFilterLists() {
    const dset = new Set<string>();
    const tset = new Set<string>();
    for (const d of this.docs) {
      if (d.creationDate) dset.add(d.creationDate.split('T')[0]);
      const m = (d.contentType || '').toLowerCase();
      if (m.includes('pdf')) tset.add('PDF');
      else if (m.includes('image')) tset.add('Image');
      else if (m.includes('word') || m.includes('officedocument') || m.includes('msword')) tset.add('Document');
      else if (m) tset.add('Other');
    }
    this.dates = Array.from(dset).sort((a, b) => b.localeCompare(a));
    this.types = Array.from(tset).sort();
  }

  // header handlers
  onSearch(q: string) { this.query = q || ''; this.applyFilters(); }
  onFilterChanged(f: { date: string, type: string }) { this.appliedDate = f.date; this.appliedType = f.type; this.applyFilters(); }
  onUploaded() { this.load(); }

  applyFilters() {
    let filtered = this.docs.slice();

    if (this.query) {
      const q = this.query.toLowerCase();
      filtered = filtered.filter(d => (d.data || '').toLowerCase().includes(q) || (d.fileName || '').toLowerCase().includes(q));
    }
    if (this.appliedDate) {
      filtered = filtered.filter(d => d.creationDate && d.creationDate.startsWith(this.appliedDate));
    }
    if (this.appliedType) {
      filtered = filtered.filter(d => {
        const m = (d.contentType || '').toLowerCase();
        if (this.appliedType === 'PDF') return m.includes('pdf');
        if (this.appliedType === 'Image') return m.includes('image');
        if (this.appliedType === 'Document') return m.includes('word') || m.includes('officedocument') || m.includes('msword');
        if (this.appliedType === 'Other') return !!m && !m.includes('pdf') && !m.includes('image') && !m.includes('word') && !m.includes('officedocument');
        return true;
      });
    }

    this.pageIndex = 0;
    this.pageDocs = filtered.slice(0, this.pageSize);
  }

  updatePage() {
    if (!Array.isArray(this.docs) || this.docs.length === 0) { this.pageDocs = []; return; }
    const start = this.pageIndex * this.pageSize;
    this.pageDocs = this.docs.slice(start, start + this.pageSize);
  }

  // show confirm dialog
  onDeleteRequest(id: string) {
    this.confirmTargetId = id;
    const doc = this.docs.find(d => d.id === id);
    this.confirmTargetName = doc ? doc.fileName : '';
    this.confirmVisible = true;
  }

  // confirmMessage is bound in the template to avoid complex template expressions
  get confirmMessage(): string {
    const name = this.confirmTargetName || '';
    return `Are you sure you want to permanently delete "${name}"?`;
  }

  // called when user confirms in the dialog
  confirmDelete() {
    const id = this.confirmTargetId;
    if (!id) {
      this.closeConfirm();
      return;
    }
    this.svc.delete(id).subscribe({
      next: () => {
        this.closeConfirm();
        this.load();
      },
      error: (err) => {
        console.error('delete error', err);
        alert('Failed to delete the file.');
        this.closeConfirm();
      }
    });
  }

  closeConfirm() {
    this.confirmVisible = false;
    this.confirmTargetId = null;
    this.confirmTargetName = '';
  }

  openViewer(doc: DocumentDto) { this.viewerDoc = doc; this.viewerVisible = true; }
  closeViewer() { this.viewerVisible = false; this.viewerDoc = undefined; }

  pageNext() { if (this.pageIndex < this.totalPages - 1) { this.pageIndex++; this.updatePage(); } }
  pagePrev() { if (this.pageIndex > 0) { this.pageIndex--; this.updatePage(); } }
  get totalPages() { return Math.max(1, Math.ceil((this.docs?.length || 0) / this.pageSize)); }
}


