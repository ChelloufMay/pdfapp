import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FileCard } from './file-card';

describe('FileCard', () => {
  let component: FileCard;
  let fixture: ComponentFixture<FileCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FileCard]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FileCard);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
