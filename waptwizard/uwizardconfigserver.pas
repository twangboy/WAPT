unit uwizardconfigserver;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, FileUtil, Forms, Controls, Graphics, Dialogs, uwizard,
  ComCtrls, ExtCtrls, StdCtrls,
  uwizardconfigserver_data,
  WizardControls;


type


  { TWizardConfigServer }


  TWizardConfigServer = class(TWizard)
    procedure FormClose(Sender: TObject; var CloseAction: TCloseAction);
    procedure FormCloseQuery(Sender: TObject; var CanClose: boolean);
    procedure FormCreate(Sender: TObject); override;
    procedure FormShow(Sender: TObject);

  private

    m_data : TWizardConfigServerData;


  public

    function data() : Pointer; override; final;

  end;

var
  WizardConfigServer: TWizardConfigServer;

implementation

{$R *.lfm}

uses


  uwizardconfigserver_console,
  uwizardconfigserver_console_package_create_new_key,
  uwizardconfigserver_password,
  uwizardconfigserver_console_buildagent,
  uwizardconfigserver_console_package_use_existing_key,
  uwizardconfigserver_finish,
  uwizardconfigserver_postsetup,
  uwizardconfigserver_console_keyoption,
  uwizardconfigserver_console_server,
  uwizardconfigserver_server_options,
  uwizardconfigserver_welcome,
  uwizardutil,
  waptcommon;



{ TWizardConfigServer }
procedure TWizardConfigServer.FormCreate(Sender: TObject);
begin
  inherited;

  data_init( @m_data );


end;

procedure TWizardConfigServer.FormShow(Sender: TObject);
begin
end;

procedure TWizardConfigServer.FormClose(Sender: TObject; var CloseAction: TCloseAction);
var
  b : boolean;
begin
  b := self.WizardManager.PageByName(PAGE_FINISHED).Index  = WizardManager.PageIndex;
  if b and self.m_data.launch_console then
    self.launch_console();
end;

procedure TWizardConfigServer.FormCloseQuery(Sender: TObject; var CanClose: boolean);
const
  MSG : String = 'Configuration is not terminated, Are you sure you want to exit ?';
begin
  if not m_data.can_close then
   CanClose := self.show_question_yesno(MSG);
end;


function TWizardConfigServer.data(): Pointer;
begin
  exit( @m_data );
end;



end.

