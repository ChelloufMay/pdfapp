// frontend/src/app/shared/components/document-viewer/document-viewer.component.ts
// Viewer modal component: fetches keyword stats from server and displays them.
// This component is standalone and uses CommonModule.

import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentService, DocumentDto, KeywordStat } from '../../../core/services/document.service';

@Component({
  selector: 'app-document-viewer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './document-viewer.component.html',
  styleUrls: ['./document-viewer.component.scss']
})
export class DocumentViewerComponent implements OnChanges {
  // Input doc may be undefined/null; template uses `*ngIf="visible && doc as d"` to guard.
  @Input() doc?: DocumentDto | null;
  @Input() visible = false;
  @Output() closed = new EventEmitter<void>();

  stats: KeywordStat[] = [];
  loading = false;

  constructor(private svc: DocumentService) {}

  ngOnChanges(changes: SimpleChanges) {
    // When viewer becomes visible and doc exists -> load stats.
    if ((changes['visible'] && this.visible) || (changes['doc'] && this.visible)) {
      if (this.doc) {
        this.loadStats();
      } else {
        this.stats = [];
      }
    }
  }

  // Get keyword stats from backend (/keyword-stats/)
  loadStats() {
    if (!this.doc) { this.stats = []; return; }
    this.loading = true;
    this.svc.getKeywordStats(this.doc.id).subscribe({
      next: (s) => { this.stats = Array.isArray(s) ? s : []; this.loading = false; },
      error: (err) => {
        console.error('keyword-stats error', err);
        this.stats = [];
        this.loading = false;
      }
    });
  }

  // Copy "word (percent%)" list to clipboard
  copyKeywordsToClipboard(): void {
    if (!this.stats || this.stats.length === 0) {
      alert('No keywords to copy.');
      return;
    }
    const text = this.stats.map(k => `${k.word} (${k.percent}%)`).join('\n');
    navigator.clipboard.writeText(text).then(() => {
      // small user feedback
      alert('Keywords copied to clipboard');
    }, () => {
      alert('Copy failed');
    });
  }

  close(): void {
    this.closed.emit();
  }
}
