import 'package:flutter/material.dart';
import '../core/routes/app_routes.dart';
import '../services/api_client.dart';

class WomenOnlySwitch extends StatefulWidget {
  const WomenOnlySwitch({super.key, required this.value, required this.onChanged, required this.publishing});
  final bool value;
  final ValueChanged<bool> onChanged;
  final bool publishing;
  @override
  State<WomenOnlySwitch> createState() => _WomenOnlySwitchState();
}
class _WomenOnlySwitchState extends State<WomenOnlySwitch> {
  String? gender;
  bool loading = true;
  String? error;
  @override
  void initState() {super.initState();load();}
  Future<void> load() async {
    try {
      final profile = await ApiClient.instance.profile();
      if(mounted)setState(() {gender=profile['gender']?.toString();loading=false;error=null;});
    } on ApiException catch(e) {if(mounted)setState(() {error=e.message;loading=false;});}
  }
  @override
  Widget build(BuildContext context) => Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
    SwitchListTile(
      contentPadding:EdgeInsets.zero,
      title:Text(widget.publishing ? 'Solo mujeres · conductora y pasajeras' : 'Buscar viajes Solo mujeres'),
      subtitle:Text(loading ? 'Consultando tu perfil…' : gender=='FEMALE'
        ? widget.publishing ? 'Solo podrán reservar mujeres. Cada pasajera solicita un asiento desde su cuenta.' : 'Muestra viajes exclusivos para mujeres, publicados por conductoras.'
        : gender=='MALE' ? 'Esta modalidad está disponible para mujeres.' : 'Completa Hombre/Mujer en Mi perfil para consultar tu acceso.'),
      value:widget.value,
      onChanged:!loading && error==null && gender=='FEMALE' ? widget.onChanged : null,
    ),
    if(!loading && gender==null && error==null)TextButton(onPressed:() async {
      await Navigator.pushNamed(context,AppRoutes.profile);
      if(mounted)await load();
    },child:const Text('COMPLETAR DATO EN MI PERFIL')),
    if(error!=null)TextButton(onPressed:load,child:Text('Reintentar: $error')),
    if(widget.value)const Padding(padding:EdgeInsets.only(bottom:12),child:Text('Se utiliza el dato declarado en el perfil; no equivale a una verificación adicional de identidad.')),
  ]);
}
