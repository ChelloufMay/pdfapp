// src/app/core/services/document.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DocumentDto {
  id: string;
  fileName: string;
  creationDate: string;
  data: string;
  fileUrl: string;
  fileSize: number;
  contentType: string;
}

@Injectable({ providedIn: 'root' })
export class DocumentService {
  // Use full URL or '/api/documents/' if using Angular proxy
  private base = 'http://127.0.0.1:8000/api/documents/';

  constructor(private http: HttpClient) {}

  list(): Observable<DocumentDto[]> {
    return this.http.get<DocumentDto[]>(this.base);
  }

  get(id: string) {
    return this.http.get<DocumentDto>(`${this.base}${id}/`);
  }

  delete(id: string) {
    return this.http.delete(`${this.base}${id}/`);
  }

  upload(file: File) {
    const fd = new FormData();
    fd.append('file', file, file.name);
    return this.http.post<DocumentDto>(this.base, fd);
  }

  // optional search endpoint (if your backend provides it)
  search(q: string) {
    const url = `${this.base}search/?q=${encodeURIComponent(q)}`;
    return this.http.get<DocumentDto[]>(url);
  }
}
