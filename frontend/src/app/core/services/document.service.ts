// frontend/src/app/core/services/document.service.ts
// Service responsible for talking to the Django backend API.
//
// Make sure the base path matches your proxy or deployment. It expects
// endpoints like: GET /api/documents/ and GET /api/documents/<id>/keyword-stats/

import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

// keyword stat returned by backend: contains percent computed server-side
export interface KeywordStat {
  word: string;
  score: number;
  percent: number;
}

// Document DTO returned by the backend API
export interface DocumentDto {
  id: string;
  fileName: string;
  creationDate: string;
  // data: raw extracted text (if used)
  data?: string | null;
  // keywords list (unique cleaned keywords) — may or may not be present in UI
  keywords?: string[] | null;
  // keyword_scores mapping may be present
  keyword_scores?: { [k: string]: number } | null;
  language?: string | null;
  fileUrl?: string | null;
  fileSize?: number | null;
  contentType?: string | null;
}

@Injectable({ providedIn: 'root' })
export class DocumentService {
  // Base API path — adjust if your Django is served under a different prefix
  private base = '/api/documents/';

  constructor(private http: HttpClient) {}

  // List documents. Handles paginated or non-paginated responses.
  list(): Observable<DocumentDto[]> {
    return this.http.get<any>(this.base).pipe(
      map(res => {
        // If DRF Page results format
        if (res && Array.isArray(res.results)) return res.results as DocumentDto[];
        // If API returns an array directly
        if (Array.isArray(res)) return res as DocumentDto[];
        // Unexpected shape -> empty array
        return [] as DocumentDto[];
      }),
      catchError(err => {
        console.error('DocumentService.list error', err);
        return of([] as DocumentDto[]);
      })
    );
  }

  get(id: string) {
    return this.http.get<DocumentDto>(`${this.base}${id}/`);
  }

  delete(id: string) {
    return this.http.delete<void>(`${this.base}${id}/`);
  }

  // Simple upload (returns created DocumentDto)
  upload(file: File) {
    const fd = new FormData();
    fd.append('file', file, file.name);
    return this.http.post<DocumentDto>(this.base, fd);
  }

  // Upload with progress events (used by upload dialog)
  uploadWithProgress(file: File): Observable<HttpEvent<DocumentDto>> {
    const fd = new FormData();
    fd.append('file', file, file.name);
    return this.http.post<DocumentDto>(this.base, fd, { reportProgress: true, observe: 'events' as any });
  }

  // New: fetch keyword statistics (word, score, percent) from backend
  getKeywordStats(id: string): Observable<KeywordStat[]> {
    return this.http.get<KeywordStat[]>(`${this.base}${id}/keyword-stats/`);
  }

  // Download endpoint helper
  downloadEndpoint(id: string) {
    return `/api/documents/${id}/download/`;
  }
}
