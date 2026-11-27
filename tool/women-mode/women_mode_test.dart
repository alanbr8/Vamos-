import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:vamos_app/screens/auth/register_screen.dart';
import 'package:vamos_app/screens/trips/search_trip_screen.dart';

void main() {
  test('el resultado conserva Solo mujeres sin reinterpretar cadenas', () {
    expect(tripMatchFromApi({'womenOnly':true},'07:00').womenOnly,isTrue);
    expect(tripMatchFromApi({'womenOnly':'false'},'07:00').womenOnly,isFalse);
    expect(tripMatchFromApi({},'07:00').womenOnly,isFalse);
  });
  testWidgets('el registro pregunta Hombre/Mujer sin asignarlo por defecto', (tester) async {
    await tester.pumpWidget(const MaterialApp(home:RegisterScreen()));
    final picker=find.byWidgetPredicate((widget)=>widget is DropdownButtonFormField<String> && widget.decoration.labelText=='¿Eres hombre o mujer?');
    expect(picker,findsOneWidget);
    expect(tester.widget<DropdownButtonFormField<String>>(picker).initialValue,isNull);
    final form=tester.state<FormState>(find.byType(Form));
    expect(form.validate(),isFalse);
    await tester.pump();
    expect(find.text('Selecciona una opción'),findsOneWidget);
  });
}
