// document-viewer.component.ts
// Viewer for a Document that displays the computed keywords (word, count, percent).
// This file is defensive about the shape of `doc.data` so it won't break if the backend
// returns a string, null, or an array.

import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentDto } from '../../../core/services/document.service';

type KW = { word: string; count: number; percent: number };

@Component({
  selector: 'app-document-viewer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './document-viewer.component.html',
  styleUrls: ['./document-viewer.component.scss']
})
export class DocumentViewerComponent {
  @Input() doc?: DocumentDto | null;
  @Input() visible = false;
  @Output() closed = new EventEmitter<void>();

  // Parse doc.data into a stable array of keywords (KW[]).
  // Acceptable incoming shapes:
  // - Array of objects: [{word, count, percent}, ...]
  // - JSON string of that array
  // - null/undefined/other -> return []
  private parseKeywords(): KW[] {
    if (!this.doc) return [];

    const raw: unknown = (this.doc as any).data;

    // Already an array? normalize items
    if (Array.isArray(raw)) {
      return raw.map((k: any) => this.normalizeKeyword(k));
    }

    // If it's a string, try to parse JSON
    if (typeof raw === 'string' && raw.length > 0) {
      try {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          return parsed.map((k: any) => this.normalizeKeyword(k));
        }
        // if parsed is an object with keys, try to turn into array
      } catch (e) {
        // not JSON — nothing we can do; fall through to empty result
      }
    }

    // fallback empty
    return [];
  }

  // Ensure each item has the expected fields with correct types
  private normalizeKeyword(k: any): KW {
    const word = (k && (k.word ?? k[0])) ? String(k.word ?? k[0]) : '';
    const count = (k && (k.count ?? k[1])) ? Number(k.count ?? k[1]) : 0;
    const percent = (k && (k.percent ?? k[2])) ? Number(k.percent ?? k[2]) : 0;
    return { word, count, percent };
  }

  // Getter used by template for safe iteration
  get keywordsList(): KW[] {
    return this.parseKeywords();
  }

  // Copies a human-friendly keywords list to clipboard
  copyKeywordsToClipboard(): void {
    const kws = this.keywordsList;
    if (!kws || kws.length === 0) {
      alert('No keywords to copy.');
      return;
    }
    const text = kws.map(k => `${k.word} (${k.percent}%)`).join('\n');
    navigator.clipboard.writeText(text).then(() => {
      alert('Keywords copied to clipboard');
    }, () => {
      alert('Copy failed');
    });
  }

  close(): void {
    this.closed.emit();
  }
}

