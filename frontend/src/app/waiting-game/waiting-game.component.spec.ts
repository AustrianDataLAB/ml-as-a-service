import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WaitingGameComponent } from './waiting-game.component';

describe('WaitingGameComponent', () => {
  let component: WaitingGameComponent;
  let fixture: ComponentFixture<WaitingGameComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [WaitingGameComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(WaitingGameComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
