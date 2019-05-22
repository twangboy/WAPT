unit uVisLogin;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, FileUtil, Forms, Controls, Graphics, Dialogs, StdCtrls,
  Buttons, ExtCtrls;

type

  { TVisLogin }

  TVisLogin = class(TForm)
    ButOk: TBitBtn;
    ButCancel: TBitBtn;
    EdUsername: TEdit;
    EdPassword: TEdit;
    ImageWarning: TImage;
    ImgWarning: TImage;
    LogoLogin: TImage;
    Panel1: TPanel;
    PanelLogin: TPanel;
    StaticText1: TStaticText;
    StaticText2: TStaticText;
    WarningText: TStaticText;
    procedure FormCreate(Sender: TObject);
    procedure FormShow(Sender: TObject);
  private

  public

  end;

var
  VisLogin: TVisLogin;

implementation

uses waptcommon;

{$R *.lfm}

{ TVisLogin }

procedure TVisLogin.FormShow(Sender: TObject);
begin
  MakeFullyVisible();
  EdPassword.SetFocus;
end;

procedure TVisLogin.FormCreate(Sender: TObject);
begin
  {$ifdef ENTERPRISE }
  if FileExists(WaptBaseDir+'\templates\waptself-logo.png') then
    LogoLogin.Picture.LoadFromFile(WaptBaseDir+'\templates\waptself-logo.png')
  else
    LogoLogin.Picture.LoadFromResourceName(HINSTANCE,'ENTERPRISE-200PX');
  {$endif}
  if Screen.PixelsPerInch <> 96 then
  begin
     LogoLogin.AutoSize:=false;
     LogoLogin.AntialiasingMode:=amOn;
     ImageWarning.AutoSize:=false;
     ImageWarning.AntialiasingMode:=amOn;
  end;
end;

end.

